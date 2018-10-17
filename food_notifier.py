import logging
import os
import threading
import time
import requests
from stat import S_ISREG, ST_CTIME, ST_MODE

import numpy as np
from fastai.conv_learner import ConvLearner
from fastai.dataset import ImageClassifierData
from fastai.dataset import open_image
from fastai.transforms import tfms_from_model
from torchvision.models import resnet34

from slack_integrator import Slack

log = logging.getLogger(__name__)


class FoodNotifier(object):

    def __init__(self, event):
        self.exit_event = event
        self.last_notification_sent = 0
        self.notification_threshold = 60 * 5

        PATH = os.getcwd()
        self.sz = 224
        self.arch = resnet34
        self.data = ImageClassifierData.from_paths(PATH, tfms=tfms_from_model(self.arch, sz))
        self.learn = ConvLearner.pretrained(self.arch, self.data, precompute=True)
        self.learn.load('224_all')
        self.trn_tfms, self.val_tfms = tfms_from_model(self.arch, self.sz)

    def run(self):
        threading.Thread(target=self.food_detector).run()
        #threading.Thread(target=self.images_rsync).run()

    def get_last_image(self):
        name = '%s.jpg' % str(time.time())
        f = open(name, 'wb')
        f.write(requests.get('http://172.16.1.151:5000/live').content)
        f.close()
        return name

    def is_food_onimage(self, image):
        im = self.val_tfms(open_image(f'{image}'))
        log_pred = self.learn.predict_array(im[None])
        probs = np.exp(log_pred[:, 1])
        return probs[0]

    def images_rsync(self):
        while not self.exit_event.is_set():
            os.system(
                "rsync -avz --remove-source-files -e ssh 172.16.1.151:/usr/web/food_delivery_detector/images camera/")

    def food_detector(self):
        while not self.exit_event.is_set():
            image = self.get_last_image()
            if image and \
                    self.last_notification_sent - time.time() > self.notification_threshold and \
                    self.is_food_onimage(image):
                self.send_food_is_here(image)

            time.sleep(1)

    def send_food_is_here(self, image):
        try:
            details = u'Anonymous User'
            deal_link = u''
            piplbi_link = u''

            attachment = {
                # "fallback": u"{} {}".format(file_description, deal_link),
                "pretext": u"Food is here",
                "title": "Fresh food is here",
                "text": "Fresh food is here",
                "color": "#4596E8"
            }

            # if deal:
            #     attachment.update({
            #         "title_link": "https://pipl.pipedrive.com/deal/{}".format(deal.pipedrive_id),
            #         "text": u"{} - for more information {} {} ".format(file_description, deal_link, piplbi_link)
            #     })

            Slack.send_message('food_court', attachments=[attachment])
        except:
            log.exception("Error sending slack message")
        else:
            self.last_notification_sent = time.time()


event_exit = threading.Event()
food_notifier = FoodNotifier(event_exit)

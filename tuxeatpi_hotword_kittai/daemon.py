"""Module defining Hotword component based on Snowboy"""
import logging
import time
import wave

from tuxeatpi_common.daemon import TepBaseDaemon
from tuxeatpi_common.error import TuxEatPiError
from tuxeatpi_common.message import Message, is_mqtt_topic

from tuxeatpi_hotword_kittai.libs import snowboydecoder

LANGUAGES = {"en_US": "eng-USA",
             "fr_FR": "fra-FRA"}


class HotWord(TepBaseDaemon):
    """HotWord SnowBoy based component class

    This component waits for hotword and triggers nlu/audio topic message
    """
    def __init__(self, name, workdir, intent_folder, dialog_folder, logging_level=logging.INFO):
        self.name = "hotword"
        TepBaseDaemon.__init__(self, name, workdir, intent_folder, dialog_folder, logging_level)
        # Decoder
        self.disabled = False
        # Get from settings
        self._answer_sound_path = None
        self.sensitivity = 0.5
        self._model_file = None
        self.detector = None

    def _answering(self):
        """Play the hotword confirmation sound"""
        f_ans = wave.open(self._answer_sound_path, "rb")
        self._paudio = self.detector.audio
        stream = self._paudio.open(format=self._paudio.get_format_from_width(f_ans.getsampwidth()),
                                   channels=f_ans.getnchannels(),
                                   rate=f_ans.getframerate(),
                                   output=True)
        data = f_ans.readframes(1024)
        while data:
            stream.write(data)
            data = f_ans.readframes(1024)
        # Close file
        f_ans.close()
        # Close stream
        stream.stop_stream()
        stream.close()

    def _wake_up(self):
        """Wake up work capability

        Answer to the speaker and create a transmission for audio nlu
        """
        if not self.disabled:
            # answering
            self._answering()
            # create tranmission for audio nlu
            data = {"arguments": {"context_tag": "general"}}
            message = Message(topic="nlu/audio", data=data, context="general")
            self.publish(message)

    def set_config(self, config):
        """Save the configuration and reload the daemon"""
        # TODO improve this ? can be factorized ?
        for attr in ('sensitivity', 'sound_file', 'model_file'):
            if attr not in config.keys():
                self.logger.error("Missing parameter {}".format(attr))
                return False
        # Set params
        self._model_file = config.get('model_file')
        self._answer_sound_path = config.get("sound_file")
        if self.sensitivity != config.get("sensitivity"):
            self.sensitivity = float(config.get("sensitivity"))
            if self.detector is not None:
                self.detector.terminate()
            # Create a new detector
            self.detector = snowboydecoder.HotwordDetector(self._model_file,
                                                           self.logger,
                                                           sensitivity=self.sensitivity)

        return True

    @is_mqtt_topic("help")
    def help_(self):
        pass

    @is_mqtt_topic("shutdown")
    def shutdown(self):
        self.detector.terminate()
        super(HotWord, self).shutdown()

    @is_mqtt_topic("reload")
    def reload(self):
        pass

    @is_mqtt_topic("disable")
    def disable(self):
        """Disable hotword listening"""
        self.logger.info("Disabling listening for hotword")
        self.disabled = True

    @is_mqtt_topic("enable")
    def enable(self):
        """Enable hotword listening"""
        self.logger.info("Enabling listening for hotword")
        self.disabled = False

    def main_loop(self):
        """Main Loop"""
        if self.detector is not None:
            self.detector.start(detected_callback=self._wake_up,
                                sleep_time=0.03)
        else:
            self.logger.warning("Hotword detector not started, wait for settings")
            time.sleep(1)


class HotWordError(TuxEatPiError):
    """Base class for hotword exceptions"""
    pass

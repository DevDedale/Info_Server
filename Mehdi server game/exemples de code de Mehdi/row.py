from game.logic import GameLogic
from game.ui.base import Base, BaseButton, BasePushButton
from game.states import State
import json

def helper_dispatch_state_or(obj):
    if isinstance(obj,State):
        return obj,None
    else:
        return None,obj

def helper_uid_or_none(s):
    if s is None:
        return None
    else:
        return s.uid

class NotARowElement(Exception):
    pass

class RowElement(Base):
    
    @staticmethod
    def check_instances(es):
        Base.check_instances(es, RowElement, NotARowElement)

class RowStaticText(RowElement):
    vue_component = "ui-row-static-text"

    def __init__(self, text=None):
        RowElement.__init__(self)

        self.text = text

    def get_options_serialized(self):
        return { 
            **super().get_options_serialized(),
            'text': self.text
        }

class RowDynamicText(RowElement):
    vue_component = "ui-row-dynamic-text"

    def __init__(self, state_or_text):
        RowElement.__init__(self)

        self.state, self.static_text = helper_dispatch_state_or(state_or_text)

    def get_options_serialized(self):
        return {
            **super().get_options_serialized(),
            'static_text': self.static_text,
            'uid': helper_uid_or_none(self.state),
        }

class RowChecklist(RowElement):
    vue_component = "ui-row-checklist"

    def __init__(self, title, values):
        RowElement.__init__(self)
        self.title = title
        self.values = values

    def get_options_serialized(self):
        return {
            **super().get_options_serialized(),
            'title': self.title,
            'values': [
                {'uid':state.uid, 'text':text} for (state,text) in self.values
            ],
        }

class RowLedBar(RowElement):
    vue_component = "ui-row-ledbar"

    def __init__(self, title, values, fill = False):
        RowElement.__init__(self)
        self.title = title
        self.values = values
        self.fill = fill

    def get_options_serialized(self):
        return { 
            **super().get_options_serialized(),
            'title': self.title,
            'fill': self.fill,
            'values': [
                {'uid':state.uid, 'text':text} for (state,text) in self.values
            ]
        }

class RowPasscode(RowElement):
    vue_component = "ui-row-passcode"

    def __init__(self, title, state, expected=None):
        RowElement.__init__(self)
        self.title = title
        self.state = state
        self.expected = expected

    def get_options_serialized(self):
        return {
            **super().get_options_serialized(),
            'title': self.title,
            'uid': self.state.uid,
            'expected': self.expected,
        }

class RowButton(BaseButton,RowElement):
    vue_component = "ui-row-button"

    def __init__(self, text, big=False, color=None, click=None, feedback_state=None):
        RowElement.__init__(self)
        BaseButton.__init__(self,text,click)
        self.text = text
        self.color = color
        self.big = big
        self.feedback_state = feedback_state

    def get_options_serialized(self):
        return {
            **super().get_options_serialized(),
            'color': self.color,
            'big': self.big,
            'feedback_uid': helper_uid_or_none(self.feedback_state),
        }        


class RowPushButton(BasePushButton,RowElement):
    vue_component = "ui-row-push-button"

    def __init__(self, text, big=False, color=None, push=None):
        RowElement.__init__(self)
        BasePushButton.__init__(self,text,push)
        self.color = color
        self.big = big

    def get_options_serialized(self):
        return {
            **super().get_options_serialized(),
            'color': self.color,
            'big': self.big,
        }

class RowDoor(RowElement, BaseButton):
    vue_component = "ui-door"

    def __init__(self, text, state, click, description):
        RowElement.__init__(self)
        BaseButton.__init__(self, text, click)

        self.state = state
        self.description = description

    def get_options_serialized(self):
        return {
            **super(RowElement, self).get_options_serialized(),
            **super(BaseButton, self).get_options_serialized(),
            'uid': self.state.uid,
            'description': self.description,
        }

class RowImageBlock(RowElement):
    vue_component = "ui-row-image-block"

    def __init__(self, title, legend, image, image_size=None):
        RowElement.__init__(self)

        self.title = title
        
        if image_size is None:
            image_size = (None,None)
        self.image_width, self.image_height = image_size
        self.legend_state, self.legend_static_text = helper_dispatch_state_or(legend)
        self.image_state, self.image_static_url = helper_dispatch_state_or(image)


    def get_options_serialized(self):
        return {
            **super().get_options_serialized(),
            'title': self.title,
            'legend_uid': helper_uid_or_none(self.legend_state),
            'legend_static_text': self.legend_static_text,
            'image_uid': helper_uid_or_none(self.image_state),
            'image_static_url': self.image_static_url,
            'image_width': self.image_width,
            'image_height': self.image_height,
        }

class RowSlider(RowElement):
    vue_component = "ui-row-slider"

    def __init__(self, state, label=None,
            vmin=None, vmax=None, vstep=None,
            prepend_icon=None, append_icon=None,
            unit=None):

        RowElement.__init__(self)

        self.state = state
        self.label = label
        self.vmin = vmin
        self.vmax = vmax
        self.vstep = vstep
        self.prepend_icon = prepend_icon
        self.append_icon = append_icon
        self.unit = unit

        # wrap standard UI callback to update state value
        def on_ui_callback(v):
            GameLogic().log_server("user set {} ({}) to {}".format(
                str(self.__class__.__name__),
                self.label,
                v,
            ))
            self.state.set(v)
        self.register_new_callback('callback',on_ui_callback)

    def get_options_serialized(self):
        return {
            **super().get_options_serialized(),
            'label': self.label,
            'min': self.vmin,
            'max': self.vmax,
            'step': self.vstep,
            'prepend_icon': self.prepend_icon,
            'append_icon': self.append_icon,
            'unit': self.unit,
            'uid': self.state.uid,
        }

class RowDialogInput(RowElement):
    vue_component = "ui-row-dialog-input"

    def __init__(self, label=None, input_label=None, callback=None,
                        color=None, big=False):
        RowElement.__init__(self)

        self.label = label
        self.input_label = input_label
        self.color = color
        self.big = big

        self.callback_uid = None
        if callback:
            def on_ui_callback(text):
                GameLogic().log_server("user sent \"{}\" through {} ({})".format(
                    text,
                    str(self.__class__.__name__),
                    self.label,
                ))
                callback(text)
            self.register_new_callback('callback', on_ui_callback)

    def get_options_serialized(self):
        return {
            **super().get_options_serialized(),
            'label': self.label,
            'input_label': self.input_label,
            'color': self.color,
            'big': self.big,
        }

class RowDialog(RowElement):
    vue_component = "ui-row-dialog"

    def __init__(self, label=None, title=None, content=None, big=False, color=None, fullscreen=False):
        RowElement.__init__(self)

        self.content = [] if content is None else content
        self.label = label
        self.title = title
        self.big = big
        self.color = color
        self.fullscreen = fullscreen

    def get_options_serialized(self):
        cserialized = []
        for c in self.content:
            cserialized.append(c.get_serialized())
        return {
            **super().get_options_serialized(),
            'label': self.label,
            'content': cserialized,
            'title': self.title,
            'big': self.big,
            'fullscreen': self.fullscreen,
            'color': self.color
        }


import tempfile
from misc.file import FileWriter

class RowUploader(RowElement):
    vue_component = "ui-row-uploader"

    def __init__(self, callback=None, cache_directory=None, accept_mime=None):
        """
            @param callback: callback which returns (bool, msg)

            def on_uploaded(original_filename, filezize, file_path):
               if ......:
                    return True, None
               else:
                return False, 'The file is invalid'
        """

        RowElement.__init__(self)

        self.register_new_callback('callback', self.upload_callback)
        self.callback = callback
        self.accept_mime = accept_mime

        # setup file writer
        if cache_directory is None:
            cache_directory = tempfile.gettempdir()
        self.fw = FileWriter(cache_directory)

    def on_upload_complete(self, filename, filesize, original_filename):
        GameLogic().log_server("user uploaded '{}' ({} bytes) to '{}'".format(
            original_filename,
            filesize,
            filename
        ))
        if self.callback:
            return self.callback(filename, filesize, original_filename)
        return True, None

    def upload_callback(self, action, arguments):
        if action == "prepare":

            filesize = arguments.get('filesize',None)
            if filesize is None:
                logging.error("Missing key 'filesize' in upload callback arguments")

            filename = self.fw.reserve(filesize)
            return {'filename':filename}

        elif action == "chunk":

            filename = arguments.get('filename', None)
            if filename is None:
                logging.error("Missing key 'filename' in upload callback arguments")
                return
            position = arguments.get('position',None)
            if position is None:
                logging.error("Missing key 'position' in upload callback arguments")
                return
            chunk = arguments.get('chunk',None)
            if chunk is None:
                logging.error("Missing key 'chunk' in upload callback arguments")
                return
            self.fw.write(filename, position, chunk)
            return {'result':'ok'}

        elif action == "complete":
            filename = arguments.get('filename', None)
            if filename is None:
                logging.error("Missing key 'filename' in upload callback arguments")
                return
            self.fw.complete(filename)

            original_filename = arguments.get('original_filename', None)
            if original_filename is None:
                logging.error("Missing key 'original_filename' in upload callback arguments")
                return

            filesize = arguments.get('filesize',None)
            if filesize is None:
                logging.error("Missing key 'filesize' in upload callback arguments")

            res, msg = self.on_upload_complete(filename, filesize, original_filename)
            return {
                    'result':res,
                    'message': msg
                    }


    def get_options_serialized(self):
        return {
            **super().get_options_serialized(),
            'accept': self.accept_mime,
        }

class RowUnisonMicrophone(BaseButton,RowElement):
    vue_component = "ui-row-unison-microphone"

    def __init__(self, base_url, zone, text=""):
        RowElement.__init__(self)
        self.text = text
        self.base_url = base_url
        self.zone = zone

    def get_options_serialized(self):
        return {
            **super().get_options_serialized(),
            'base_url': self.base_url,
            'zone': self.zone
        }


class RowJsonEditor(BaseButton,RowElement):
    vue_component = "ui-row-json-editor"

    def __init__(self, state, text, read_only=False, validate_callback=None):
        """
            @param state: logic state to be displayed/updated
            @param text: label of the control
            @param read_only: enable or disable editing
            @param validate_callback: callback which returns (bool, msg)

            def on_validate(data):
               if ......:
                    return True
               else:
                return False, 'The field XXX is invalid'
        """
        RowElement.__init__(self)
        self.state = state
        self.text = text
        self.read_only = read_only

        def on_ui_callback(value):
            ret = {
                'result': True,
                'message': ''
            }
            if isinstance(value, str):
                value = json.loads(value)
            if validate_callback is not None:
                res = validate_callback(value)
                if isinstance(res, tuple):
                    valid, msg = res
                    ret = {
                        'result': valid,
                        'message': msg
                    }
                else:
                    ret['result'] = res
            if ret['result']:
                GameLogic().log_server("user sent \"{}\" through {} ({})".format(
                    text,
                    str(self.__class__.__name__),
                    value
                ))
                self.state.set(value)
            else:
                GameLogic().log_warn("user sent \"{}\" through {} invalid data: {} ({})".format(
                     text,
                     str(self.__class__.__name__),
                     ret['message'],
                     value
                 ))

            return ret
        self.register_new_callback('callback', on_ui_callback)


    def get_options_serialized(self):
        return {
            **super().get_options_serialized(),
            'uid': self.state.uid,
            'read_only': self.read_only
        }


from formless import webform, annotate, iformless
from formless.webform import keyToXMLID
from nevow import compy
from nevow.tags import *

class StyleString(annotate.String):
    pass

class StylePasswordEntry(annotate.PasswordEntry):
    pass

class StylePassword(annotate.Password):
    pass

class StyleFileUpload(annotate.FileUpload):
    pass

class StyleStringRenderer(webform.BaseInputRenderer):
    def input(self, context, slot, data, name, value):
        if data.typedValue.getAttribute('hidden'):
            T="hidden"
        else:
            T="text"
        maxlength = data.typedValue.getAttribute('maxlength')
        size = data.typedValue.getAttribute('size', maxlength or 20)
        if maxlength:            
            size = min(size, maxlength)
            return slot[
                input(id=keyToXMLID(context.key), type=T, name=name, value=value,
                      _class='freeform-input-%s' % T, size=size, maxlength=maxlength)]
        else:
            return slot[
                input(id=keyToXMLID(context.key), type=T, name=name, value=value,
                      _class='freeform-input-%s' % T,size=size)]

class StylePasswordRenderer(webform.BaseInputRenderer):
    def input(self, context, slot, data, name, value):
        maxlength = data.typedValue.getAttribute('maxlength')
        size = data.typedValue.getAttribute('size', maxlength or 20)
        if maxlength:            
            return [
                input(id=keyToXMLID(context.key), name=name, type="password", _class="freeform-input-password", size=size, maxlength=maxlength),
                " Again ",
                input(name="%s____2" % name, type="password", _class="freeform-input-password", size=size, maxlength=maxlength),
                ]
        else:
            return [
                input(id=keyToXMLID(context.key), name=name, type="password", _class="freeform-input-password",size=size),
                " Again ",
                input(name="%s____2" % name, type="password", _class="freeform-input-password",size=size),
                ]


class StylePasswordEntryRenderer(webform.BaseInputRenderer):
    def input(self, context, slot, data, name, value):
        maxlength = data.typedValue.getAttribute('maxlength')
        size = data.typedValue.getAttribute('size', maxlength or 20)
        if maxlength:            
            return slot[
                input(id=keyToXMLID(context.key), type='password', name=name,
                      _class='freeform-input-password', size=size, maxlength=maxlength)]
        else:
            return slot[
                input(id=keyToXMLID(context.key), type='password', name=name,
                      _class='freeform-input-password', size=size)]
        
class StyleFileUploadRenderer(webform.BaseInputRenderer):
    def input(self, context, slot, data, name, value):
        maxlength = data.typedValue.getAttribute('maxlength')
        size = data.typedValue.getAttribute('size', maxlength or 20)
        if maxlength:            
            return slot[input(id=keyToXMLID(context.key), type="file", name=name,
                              _class='freeform-input-file', size=size, maxlength=maxlength)]            
        else:
            return slot[input(id=keyToXMLID(context.key), type="file", name=name,
                              _class='freeform-input-file', size=size)]
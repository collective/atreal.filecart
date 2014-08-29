from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
import tempfile
import os
import zipfile
import time


def filename_only(contet, field, value):
    return value.filename


def id_and_filename(content, field, value):
    return "%s-%s" % (content.getId(), value.filename)


def id_fieldname_and_filename(content, field, value):
    return "%s-%s-%s" % (content.getId(), field.__name__, value.filename)


def uid_and_filename(content, field, value):
    return "%s-%s" % (content.UID(), value.filename)


NAMING_POLICIES = [filename_only, id_and_filename,
                   id_fieldname_and_filename, uid_and_filename]


class FileCartZip(object):

    def __init__(self, request, items):
        """
        items are a list of tuples (brain, additional attachment field names)
        """
        self.request = request
        self.items = items
        path = self.createZip()
        self.downloadZip (path)

    def _addFiles(self):

        mttool = getToolByName(getSite(), 'mimetypes_registry')
        for item in self.items:
            brain = item['brain']
            additional_attachments = item['additional_attachments']
            scales = item.get('scales', None)
            if scales is None:
                scales = ['_source']

            content = brain.getObject()
            primary_field = content.getPrimaryField()
            if primary_field is not None:
                fields = [content.getPrimaryField()]
            else:
                fields = []

            for fieldname in additional_attachments:
                fields.append(content.getField(fieldname))

            for field in fields:
                fieldname = field.__name__
                value = field.get(content)
                namelist = self.zip.namelist()
                for naming_policy in NAMING_POLICIES:
                    filename = naming_policy(content, field, value)
                    if filename not in namelist:
                        break

                if (not scales) or ('_source' in scales):
                    data = str(value.data)
                    if data:
                        self.zip.writestr(filename.decode('utf-8'), data)

                for scale in scales:
                    if scale == '_source':
                        continue

                    scale_value = field.getScale(content, scale)
                    data = str(scale_value.data)
                    if not data:
                        continue

                    scale_content_type = scale_value.getContentType()
                    scale_mimetype = mttool.lookup(scale_content_type)[0]
                    if scale_content_type == value.getContentType():
                        scale_extension = value.filename.split('.', -1)[-1]
                    elif 'jpg' in scale_mimetype.extensions:
                        # non web images thumbs are in jpeg format.
                        # priority to 'jpg' extension
                        scale_extension = 'jpg'
                    else:
                        scale_extension = scale_mimetype.extensions[0]

                    scale_filename_base = filename.split('.', -1)[0]
                    scale_filename = "%s-%s.%s" % (scale_filename_base,
                                                   scale, scale_extension)
                    self.zip.writestr(scale_filename.decode('utf-8'), data)

    def createZip(self):
        fd, path = tempfile.mkstemp('.zip')
        os.close(fd)
        self.zip = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)
        self._addFiles()
        self.zip.close()
        return path

    def _cart_filename(self):
        return "cart-" + time.strftime('%y%m%d-%H%M',time.localtime()) + ".zip"

    def downloadZip(self, path):
        filename = self._cart_filename()
        RESPONSE = self.request.RESPONSE
        RESPONSE.setHeader('content-type', 'application/zip')
        RESPONSE.setHeader('content-disposition',
                           'attachment; filename="%s"' % filename)
        RESPONSE.setHeader('content-length', str(os.stat(path)[6]))

        fp = open(path, 'rb')
        while True:
            data = fp.read(32768)
            if data:
                RESPONSE.write(data)
            else:
                break

        fp.close()
        os.remove(path)


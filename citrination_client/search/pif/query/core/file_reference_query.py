from citrination_client.search.pif.query.core.base_object_query import BaseObjectQuery
from citrination_client.search.pif.query.core.field_operation import FieldOperation


class FileReferenceQuery(BaseObjectQuery):
    """
    Class to query against a Pif FileReference object.
    """

    def __init__(self, relative_path=None, mime_type=None, sha256=None, md5=None, logic=None, tags=None,
                 length=None, offset=None):
        """
        Constructor.

        :param relative_path: One or more :class:`FieldOperation` operations against the relative path field.
        :param mime_type: One or more :class:`FieldOperation` operations against the mime type field.
        :param sha256: One or more :class:`FieldOperation` operations against the sha256 field.
        :param md5: One or more :class:`FieldOperation` operations against the md5 field.
        :param logic: Logic for this filter. Must be equal to one of "MUST", "MUST_NOT", "SHOULD", or "OPTIONAL".
        :param tags: One or more :class:`FieldOperation` operations against the tags field.
        :param length: One or more :class:`FieldOperation` operations against the length field.
        :param offset: One or more :class:`FieldOperation` operations against the offset field.
        """
        super(FileReferenceQuery, self).__init__(logic=logic, tags=tags, length=length, offset=offset)
        self._relative_path = None
        self.relative_path = relative_path
        self._mime_type = None
        self.mime_type = mime_type
        self._sha256 = None
        self.sha256 = sha256
        self._md5 = None
        self.md5 = md5

    @property
    def relative_path(self):
        return self._relative_path

    @relative_path.setter
    def relative_path(self, relative_path):
        self._relative_path = self._get_object(FieldOperation, relative_path)

    @relative_path.deleter
    def relative_path(self):
        self._relative_path = None

    @property
    def mime_type(self):
        return self._mime_type

    @mime_type.setter
    def mime_type(self, mime_type):
        self._mime_type = self._get_object(FieldOperation, mime_type)

    @mime_type.deleter
    def mime_type(self):
        self._mime_type = None

    @property
    def sha256(self):
        return self._sha256

    @sha256.setter
    def sha256(self, sha256):
        self._sha256 = self._get_object(FieldOperation, sha256)

    @sha256.deleter
    def sha256(self):
        self._sha256 = None

    @property
    def md5(self):
        return self._md5

    @md5.setter
    def md5(self, md5):
        self._md5 = self._get_object(FieldOperation, md5)

    @md5.deleter
    def md5(self):
        self._md5 = None

#!/usr/bin/env python3

"""
A module for handling transparently reading encrypted source files or teplates.
"""

#  from fernetcrypt
encrypt_blocksize = 40960
decrypt_blocksize = 54712
salt_file_size = 20
magic = "#UF1#"

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from typing import Union, Callable, Dict

from jinja2 import Template


class FernetReader:
    """
    A file-like class to transparently read FernetCrypt encrypted files, falling back
    to reading plain-text files if the file is not encrypted.

    Args:
        - file_name: File to read.
        - password: Can either be a password, or a function that returns a password when
            called.

    Examples:

        def get_password():
            return "foo"


        f = FernetReader("foo.fernet", "foo")
        print(f.read())
        f = FernetReader("foo.fernet", get_password)
        print(f.read())

        with FernetReader("foo.fernet", get_password) as f:
           print(f.read())
    """

    def __init__(self, file_name: str, password: Union[str, Callable]):
        self.file_name = file_name
        self.password = password

        self._file = open(self.file_name, "rb")
        self.buffer = self._file.read(25)
        if self.buffer[20:25] == b"#UF1#":
            password = self._get_password()
            salt = base64.b85decode(self.buffer[:20])

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=960000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode("ascii")))
            self._fernet = Fernet(key)
            self._reader = self.fernet_reader

            self.buffer = b""
        else:
            self._reader = self.plaintext_reader

    def _get_password(self):
        """Returns the password for decryption."""

        if callable(self.password):
            return self.password()
        return self.password

    def fernet_reader(self, size: int = -1) -> bytes:
        while True:
            #  already have enough bytes
            if size != -1 and len(self.buffer) > size:
                ret = self.buffer[:size]
                self.buffer = self.buffer[size:]
                return ret

            data = self._file.read(decrypt_blocksize)
            if not data:
                ret = self.buffer
                self.buffer = b""
                return ret

            self.buffer += self._fernet.decrypt(data)

    def plaintext_reader(self, size: int = -1) -> bytes:
        ret = self.buffer + self._file.read(size)
        self.buffer = b""
        return ret

    def read(self, size: int = -1):
        return self._reader(size)

    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, *_):
        """Exit the runtime context and perform any necessary cleanup."""
        self._file.close()


class JinjaFernetReader:
    """
    A wrapper on top of FernetReader that will render the template contained in the file.

    Args:
        - file_name: File to read.
        - password: Can either be a password, or a function that returns a password when
            called.
        - context: Jinja context to use with rendering
        - encoding: The encoding to convert the source file binary data into str.

    Examples:

        f = JinaFernetReader("foo.fernet", "foo", {"foo": "bar"})
        print(f.read())
    """

    def __init__(
        self,
        file_name: str,
        password: Union[str, Callable],
        context: Dict[str, str],
        encoding: str = "latin-1",
    ):
        with FernetReader(file_name, password) as fp:
            self.generator = Template(fp.read().decode(encoding)).generate(context)
        self.buffer = ""

    def read(self, size: int = -1) -> str:
        while size < 0 or len(self.buffer) < size:
            try:
                self.buffer += next(self.generator)
            except StopIteration:
                break
        if size < 0:
            ret = self.buffer
            self.buffer = ""
        else:
            ret = self.buffer[:size]
            self.buffer = self.buffer[size:]

        return ret

    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, *_):
        """Exit the runtime context and perform any necessary cleanup."""
        pass

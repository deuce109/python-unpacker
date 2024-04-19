import os
import py7zr
from zipfile import ZipFile
import tarfile
import logging
import pathlib

_magic_dict = {
    "\x1f\x8b\x08":"gz",
    "\x50\x4b\x03\x04": "zip",
    "\x37\x7A\xBC\xAF\x27\x1C": "7z",
    "\xFD\x37\x7A\x58\x5A\x00": "lzma",
    "\x75\x73\x74\x61\x72": "tar"
    }

class Decompressor:
    def _find_compression_type(filename):
        logging.debug("Filename: " + filename)
        max_len = max(len(x) for x in _magic_dict)
        with open(filename, 'rb') as f:
            file_start = f.read(max_len)
        logging.info(f"File magic number: {file_start}")
        for magic, filetype in _magic_dict.items():
            if file_start.decode().startswith(magic):
                return filetype
        return None
    
    
    
    def _decompress_7z(filename, output_path):
        py7zr.SevenZipFile(filename).extractall(output_path)

    def _decompress_zip(filename, output_path):
        ZipFile(filename, 'r').extractall(output_path)

    def _decompress_lzma(filename, output_path):
        tarfile.open(filename, "r").extractall(output_path,  numeric_owner=True)

    def _decompress_gz(filename, output_path):
        tarfile.open(filename, "r").extractall(output_path)

    def _decompress_tar(filename, output_path):
        tarfile.open(filename, "r").extractall(output_path)

    def decompress(filename, output_path):
        _decompression_dict = {
            "7z": Decompressor._decompress_7z,
            "zip": Decompressor._decompress_zip,
            "lzma": Decompressor._decompress_lzma,
            "tar": Decompressor._decompress_tar,
            "gz": Decompressor._decompress_gz
        }
        filepath = os.path.abspath(filename)
        compression_type = Decompressor._find_compression_type(filepath)

        if compression_type:
            logging.info("Detected compression type: '%s'", compression_type)
            pathlib.Path(output_path).mkdir(parents=True, exist_ok=True)
            logging.debug(os.path.exists(output_path))
            _decompression_dict[compression_type](filepath, output_path)
        else:
            logging.warning("Unknown compression type: Attempting tar file decommpression")
            try:
                Decompressor._decompress_tar(filepath, output_path)
            except tarfile.ReadError as _:
                logging.info(f"Unable to read '{filepath}' please check compression type")
from bs4 import BeautifulSoup
import os, sys
import zipfile
import names
import csv
import re

class ReadZip(object):
    ''' you can pass dir name with sys.argv '''

    def __init__(self, path=None):
        self.list_zip = []
        self.list_product = []
        self.path = sys.argv[1] if len(sys.argv) == 2 else os.getcwd()
        self.EXT_PDF = 'pdf'
        self.EXT_TXT = 'txt'
        self.EXT_NFE = 'nfe'
        self.EXT_XML = 'xml'

    def get_folders(self, path=None):
        '''path where of files default self.path'''
        _path = path if path else self.path
        # return list(filter(os.path.isdir, os.listdir(_path))
        return [f for f in  os.listdir(_path) if os.path.isdir(f) and f != '.venv' ]

    def get_files(self, path=None, ext=None):
        '''return list of files in dir name'''
        _path = path if path else self.path
        files = os.listdir(_path)
        if ext:
            ext = '.%s' % ext
            files = [i for i in files if i.endswith(ext)]
        return files

    def extrat_files(self):
        '''read list of zip'''
        _files = self.get_files()
        for _file in _files:
            if os.path.isfile(_file) and _file.endswith('.zip'):
                self.list_zip.append(_file)

        # if there is no file zip in folder get out
        if len(self.list_zip) == 0:
            print('there is no zip file to work in this folder')
            return

        for zip_name in self.list_zip:
            folder_name = self.gen_name()
            os.mkdir(folder_name)
            zip = zipfile.ZipFile(zip_name)
            zip.extractall(folder_name)
            zip.close()

    def gen_name(self, is_folder=True):
        ''' generate name to folder '''
        type_file = 'folder' if is_folder else 'file'
        return  '%s_%s' % (type_file, '_'.join(names.get_full_name().lower().split()))

    def parse_client_info(self, filename):
        ''' parse client dest to dict '''
        nfe = None
        data = {}
        with open(filename) as xml:
            nfe =  xml.read()
        soup = BeautifulSoup(nfe, 'lxml')
        for element in soup.find('dest'):
            if element.string is None:
                data_key = self.get_key(element)
                _data = {}
                for el in element.findChildren():
                    key = self.get_key(el)
                    value = el.string
                    _data[key] = value
                data[data_key] = _data

            else:
                key = self.get_key(element)
                if key is not None:
                    value = element.string
                    data[key] = value
        return data

    def get_key(self, element):
        el = re.search(r"<(.*?)>",str(element))
        if el is not None:
            return el.group(1)
        return None

    def parse_producrt_list(self, filename):
        ''' parse all prodct in nfe to dict list '''
        nfe = None
        with open(filename) as xml:
            nfe = xml.read()

        soup = BeautifulSoup(nfe, 'lxml')
        items = ['cprod', 'xprod', 'ncm', 'cfop', 'vuncom', 'vprod']
        for element in soup.findAll('det'):
            data = {}
            if element.string is  None:
                for el in element.findChildren():
                    key = self.get_key(el)
                    value = el.string
                    if key in items:
                        data[key] = value
                        self.list_product.append(data)


if __name__ == '__main__':
    read_zip = ReadZip()

    read_zip.extrat_files()
    client_list = []
    folders = read_zip.get_folders()
    for dir in folders:
        current_folder = os.path.join(read_zip.path, dir)
        files = read_zip.get_files(path=current_folder ,ext=read_zip.EXT_XML)
        for file in files:
            file_path = os.path.join(current_folder, file)
            try:
                client_list.append(read_zip.parse_client_info(file_path))
                read_zip.parse_producrt_list(file_path)
            except:
                pass


    if len(read_zip.list_product) > 0:
        fieldnames = list(read_zip.list_product[0].keys())
        with open('produtos.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for prod in read_zip.list_product:
                writer.writerow(prod)

        

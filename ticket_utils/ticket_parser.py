import re
from PyPDF2 import PdfReader
from fitz import fitz
from pyzbar import pyzbar
from PIL import Image

TICKET_REGEXP = {
    'PN': r'PN[\s]?:[\s]?([\w]*)',
    'SN': r'SN[\s]?:[\s]?([\w]*)',
    'DESCRIPTION': r'DESCRIPTION[\s]?:[\s]?([\w\s]*)\n',
    'LOCATION': r'LOCATION[\s]?:[\s]?([\w]*)',
    'CONDITION': r'CONDITION[\s]?:[\s]?([\w]*)',
    'RECEIVER': r'RECEIVER#[\s]?:[\s]?([\w]*)',
    'UOM': r'UOM[\s]?:[\s]?([\w]*)',
    'EXP DATE': r'EXP DATE[\s]?:[\s]?([\d]{2}\.[\d]{2}\.[\d]{4})',
    'PO': r'PO[\s]?:[\s]?([\w]*)',
    'CERT SOURCE': r'CERT SOURCE[\s]?:[\s]?([\w]*)',
    'REC.DATE': r'REC.DATE[\s]?:[\s]?([\d]{2}\.[\d]{2}\.[\d]{4})',
    'MFG': r'MFG[\s]?:[\s]?([\w]*)',
    'BATCH': r'BATCH#[\s]?:[\s]?([\w]*)',
    'DOM': r'DOM[\s]?:[\s]?([\d]{2}\.[\d]{2}\.[\d]{4})',
    'REMARK': r'REMARK[\s]?:[\s]?([\w]*)',
    'LOT': r'LOT#[\s]?:[\s]?([\w]*)',
    'NOTES': r'NOTES[\s]?:[\s]?([\w\s]*)',
    'Qty': r'Qty[\s]?:[\s]?([\d]*)',

}


class Ticket:
    def __init__(self, ticket_path, etalon=False):
        self._is_etalon = etalon
        self._ticket_path = ticket_path
        self._ticket_name = None
        self._source_dir = None
        self._ticket_content = None
        self._barcodes = None

        self._ticket_info = {}

        self._get_ticket_name()
        self._get_source_dir()

        self._parse()

    def __str__(self):
        return f'{self._ticket_info}'

    def _get_ticket_name(self):
        self._ticket_name = self._ticket_path.split('/')[-1].split('.')[0]

    def _get_source_dir(self):
        self._source_dir = '/'.join(self._ticket_path.split('/')[:-1])

    def _parse(self):
        self._get_text_content()

        self._pdf2png()
        image = Image.open(f'{self._source_dir}/{self._ticket_name}.png')
        self._decode_barcodes(image)

        self._barcodes.sort(key=lambda x: x.rect.top)

        self.ticket_info['TITLE'] = self._ticket_content.split('\n')[0]
        self.ticket_info['MAIN BARCODE'] = self._barcodes[0]

        for k, v in TICKET_REGEXP.items():
            values = re.findall(v, self._ticket_content)
            if values:
                self.ticket_info[k] = values[0]

        self.ticket_info['TAGGED BY'] = self._barcodes[1]

    def _decode_barcodes(self, img):
        self._barcodes = pyzbar.decode(img)

    def _get_text_content(self):
        reader = PdfReader(self._ticket_path)
        page = reader.pages[0]
        text = page.extract_text()

        self._ticket_content = text

    def _pdf2png(self):
        doc = fitz.open(self._ticket_path)
        page = doc.load_page(0)
        pix = page.get_pixmap()

        output = f"{self._source_dir}/{self._ticket_name}.png"
        pix.save(output)

    @property
    def ticket_info(self):
        return self._ticket_info

    @property
    def is_etalon(self):
        return self._is_etalon

    @property
    def ticket_path(self):
        return self._ticket_path

    def __eq__(self, other):
        result = True
        if self._is_etalon ^ other._is_etalon:
            for k in self.ticket_info:
                if k not in other._ticket_info:
                    print(f'Field {k} is not in ticket')
                    result = False

            if self._ticket_info['MAIN BARCODE'].rect != other._ticket_info['MAIN BARCODE'].rect:
                print('Barcode is invalid')
                result = False

            if self._ticket_info['TAGGED BY'].rect != other._ticket_info['TAGGED BY'].rect:
                print('Barcode (TAGGED BY) is invalid')
                result = False

            return result

        elif self._is_etalon and other._is_etalon:
            return True
        else:
            return False

"""
PDF処理ツール
PDFファイルからテキストを抽出し、データベースに追加
"""

import os
from pathlib import Path
from typing import List, Dict
import PyPDF2
import pdfplumber
from PIL import Image
import pytesseract
from tqdm import tqdm
import config


class PDFProcessor:
    """PDFファイルを処理するクラス"""
    
    def __init__(self):
        """初期化"""
        self.pdf_dir = config.PDF_DIR
        
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """PyPDF2を使用してテキスト抽出"""
        text = ""
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        
        except Exception as e:
            print(f"  PyPDF2エラー: {e}")
        
        return text.strip()
    
    def extract_text_pdfplumber(self, pdf_path: str) -> str:
        """pdfplumberを使用してテキスト抽出（表も含む）"""
        text = ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # テキスト抽出
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                    
                    # 表を抽出
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            # 表を整形
                            for row in table:
                                if row:
                                    text += " | ".join([str(cell) if cell else "" for cell in row]) + "\n"
                            text += "\n"
        
        except Exception as e:
            print(f"  pdfplumberエラー: {e}")
        
        return text.strip()
    
    def extract_text_ocr(self, pdf_path: str) -> str:
        """OCRを使用してテキスト抽出（画像ベースのPDF用）"""
        text = ""
        
        try:
            # PDFを画像に変換してOCR
            # 注: この方法はpdf2imageライブラリが必要（オプション）
            # ここでは簡易版として、pdfplumberで画像抽出を試みる
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # ページを画像として取得
                    img = page.to_image(resolution=config.PDF_IMAGE_DPI)
                    
                    # PIL Imageに変換
                    pil_img = img.original
                    
                    # OCR実行
                    page_text = pytesseract.image_to_string(
                        pil_img,
                        lang=config.TESSERACT_LANG
                    )
                    
                    if page_text.strip():
                        text += f"--- Page {page_num + 1} ---\n"
                        text += page_text + "\n\n"
        
        except Exception as e:
            print(f"  OCRエラー: {e}")
            print("  注: OCRにはTesseractのインストールが必要です")
            print("     https://github.com/tesseract-ocr/tesseract")
        
        return text.strip()
    
    def process_pdf(self, pdf_path: str, use_ocr: bool = False) -> Dict:
        """PDFファイルを処理"""
        filename = os.path.basename(pdf_path)
        print(f"\n処理中: {filename}")
        
        # テキスト抽出
        text = ""
        
        # まずpdfplumberで試す（表も抽出できる）
        text = self.extract_text_pdfplumber(pdf_path)
        
        # テキストが少ない場合はPyPDF2も試す
        if len(text) < 100:
            text_pypdf2 = self.extract_text_pypdf2(pdf_path)
            if len(text_pypdf2) > len(text):
                text = text_pypdf2
        
        # それでもテキストが少ない場合はOCR（オプション）
        if use_ocr and len(text) < 100:
            print("  テキストが少ないため、OCRを試行します...")
            text = self.extract_text_ocr(pdf_path)
        
        # メタデータ
        metadata = {
            'title': filename.replace('.pdf', ''),
            'content': text,
            'url': f"file://{pdf_path}",
            'category': 'PDF',
            'source': 'pdf_file',
            'file_path': pdf_path,
            'text_length': len(text)
        }
        
        print(f"  抽出テキスト: {len(text)}文字")
        
        return metadata
    
    def process_all_pdfs(self, use_ocr: bool = False) -> List[Dict]:
        """ディレクトリ内の全PDFを処理"""
        pdf_files = list(Path(self.pdf_dir).glob("*.pdf"))
        
        if not pdf_files:
            print(f"PDFファイルが見つかりません: {self.pdf_dir}")
            return []
        
        print(f"📄 {len(pdf_files)}個のPDFファイルを処理します")
        print(f"   OCR使用: {'はい' if use_ocr else 'いいえ'}")
        
        processed_data = []
        
        for pdf_file in tqdm(pdf_files, desc="PDF処理中"):
            try:
                data = self.process_pdf(str(pdf_file), use_ocr=use_ocr)
                
                if data['text_length'] > config.MIN_CHUNK_SIZE:
                    processed_data.append(data)
                else:
                    print(f"  ⚠️  テキストが短すぎるためスキップ: {pdf_file.name}")
            
            except Exception as e:
                print(f"  ✗ エラー: {pdf_file.name} - {e}")
        
        print(f"\n✓ {len(processed_data)}個のPDFを処理しました")
        
        return processed_data


def main():
    """メイン処理 - PDFを処理してデータベースに追加"""
    import sys
    from vectordb import VectorDatabase
    
    print("=" * 80)
    print("PDF処理ツール")
    print("=" * 80)
    
    # オプション確認
    use_ocr = '--ocr' in sys.argv
    
    # PDFを処理
    processor = PDFProcessor()
    pdf_data = processor.process_all_pdfs(use_ocr=use_ocr)
    
    if not pdf_data:
        print("処理するPDFがありません")
        return
    
    # データベースに追加するか確認
    print("\nこれらのPDFをデータベースに追加しますか? (y/n): ", end="")
    response = input().strip().lower()
    
    if response == 'y':
        print("\nデータベースに追加中...")
        db = VectorDatabase()
        db.add_documents(pdf_data, source_type="pdf")
        
        print("\n✓ PDFデータをデータベースに追加しました")
    else:
        print("\nキャンセルしました")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

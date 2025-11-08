import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from services.document_parser import DocumentParser


class TestDocumentParserExtractText:
    """Test the main extract_text method with auto-detection"""

    @patch('services.document_parser.DocumentParser.extract_text_from_docx')
    def test_extract_text_docx(self, mock_extract_docx):
        mock_extract_docx.return_value = "Docx content"

        result = DocumentParser.extract_text("resume.docx")

        assert result == "Docx content"
        mock_extract_docx.assert_called_once_with("resume.docx")

    @patch('services.document_parser.DocumentParser.extract_text_from_docx')
    def test_extract_text_doc(self, mock_extract_docx):
        mock_extract_docx.return_value = "Doc content"

        result = DocumentParser.extract_text("resume.doc")

        assert result == "Doc content"
        mock_extract_docx.assert_called_once_with("resume.doc")

    @patch('services.document_parser.DocumentParser.extract_text_from_pdf')
    def test_extract_text_pdf(self, mock_extract_pdf):
        mock_extract_pdf.return_value = "PDF content"

        result = DocumentParser.extract_text("resume.pdf")

        assert result == "PDF content"
        mock_extract_pdf.assert_called_once_with("resume.pdf")

    def test_extract_text_unsupported_format(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            DocumentParser.extract_text("resume.txt")

    def test_extract_text_case_insensitive(self):
        with patch('services.document_parser.DocumentParser.extract_text_from_docx') as mock:
            mock.return_value = "Content"
            DocumentParser.extract_text("RESUME.DOCX")
            mock.assert_called_once()

        with patch('services.document_parser.DocumentParser.extract_text_from_pdf') as mock:
            mock.return_value = "Content"
            DocumentParser.extract_text("RESUME.PDF")
            mock.assert_called_once()


class TestDocumentParserPDFExtraction:
    """Test PDF text extraction"""

    @patch('services.document_parser.fitz.open')
    def test_extract_text_from_pdf_single_page(self, mock_fitz_open):
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Page 1 content"
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc

        result = DocumentParser.extract_text_from_pdf("test.pdf")

        assert result == "Page 1 content"
        mock_doc.close.assert_called_once()

    @patch('services.document_parser.fitz.open')
    def test_extract_text_from_pdf_multiple_pages(self, mock_fitz_open):
        mock_doc = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Page 2 content"

        mock_doc.__len__.return_value = 2
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
        mock_fitz_open.return_value = mock_doc

        result = DocumentParser.extract_text_from_pdf("test.pdf")

        assert "Page 1 content" in result
        assert "Page 2 content" in result
        mock_doc.close.assert_called_once()

    @patch('services.document_parser.fitz.open')
    def test_extract_text_from_pdf_empty_pages(self, mock_fitz_open):
        mock_doc = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "   \n   "
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Actual content"

        mock_doc.__len__.return_value = 2
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
        mock_fitz_open.return_value = mock_doc

        result = DocumentParser.extract_text_from_pdf("test.pdf")

        assert "Actual content" in result
        assert result.count('\n') >= 0

    @patch('services.document_parser.fitz.open')
    def test_extract_text_from_pdf_error(self, mock_fitz_open):
        mock_fitz_open.side_effect = Exception("PDF parsing error")

        with pytest.raises(Exception, match="Error parsing PDF file"):
            DocumentParser.extract_text_from_pdf("corrupt.pdf")


class TestDocumentParserDOCXExtraction:
    """Test DOCX text extraction"""

    @patch('services.document_parser.docx.Document')
    def test_extract_text_from_docx_paragraphs_only(self, mock_docx):
        mock_doc = MagicMock()
        mock_para1 = MagicMock()
        mock_para1.text = "First paragraph"
        mock_para2 = MagicMock()
        mock_para2.text = "Second paragraph"
        mock_doc.paragraphs = [mock_para1, mock_para2]
        mock_doc.tables = []
        mock_docx.return_value = mock_doc

        result = DocumentParser.extract_text_from_docx("test.docx")

        assert "First paragraph" in result
        assert "Second paragraph" in result

    @patch('services.document_parser.docx.Document')
    def test_extract_text_from_docx_with_tables(self, mock_docx):
        mock_doc = MagicMock()
        mock_para = MagicMock()
        mock_para.text = "Paragraph text"
        mock_doc.paragraphs = [mock_para]

        mock_table = MagicMock()
        mock_row = MagicMock()
        mock_cell1 = MagicMock()
        mock_cell1.text = "Cell 1"
        mock_cell2 = MagicMock()
        mock_cell2.text = "Cell 2"
        mock_row.cells = [mock_cell1, mock_cell2]
        mock_table.rows = [mock_row]
        mock_doc.tables = [mock_table]
        mock_docx.return_value = mock_doc

        result = DocumentParser.extract_text_from_docx("test.docx")

        assert "Paragraph text" in result
        assert "Cell 1" in result
        assert "Cell 2" in result

    @patch('services.document_parser.docx.Document')
    def test_extract_text_from_docx_empty_paragraphs(self, mock_docx):
        mock_doc = MagicMock()
        mock_para1 = MagicMock()
        mock_para1.text = "   "
        mock_para2 = MagicMock()
        mock_para2.text = "Actual content"
        mock_para3 = MagicMock()
        mock_para3.text = ""
        mock_doc.paragraphs = [mock_para1, mock_para2, mock_para3]
        mock_doc.tables = []
        mock_docx.return_value = mock_doc

        result = DocumentParser.extract_text_from_docx("test.docx")

        assert "Actual content" in result
        assert result.count("   ") == 0

    @patch('services.document_parser.docx.Document')
    def test_extract_text_from_docx_error(self, mock_docx):
        mock_docx.side_effect = Exception("DOCX parsing error")

        with pytest.raises(Exception, match="Error parsing DOCX file"):
            DocumentParser.extract_text_from_docx("corrupt.docx")


class TestDocumentParserHeaderExtraction:
    """Test header extraction from resume text"""

    def test_extract_header_multiple_lines(self):
        resume_text = "John Doe\njohn@email.com | 555-1234\n\nExperience\nCompany A"

        result = DocumentParser.extract_header(resume_text)

        assert "John Doe" in result
        assert "john@email.com" in result
        assert "[HEADER]" in result

    def test_extract_header_single_line(self):
        resume_text = "John Doe\n\nExperience"

        result = DocumentParser.extract_header(resume_text)

        assert "John Doe" in result
        assert "[HEADER]" in result

    def test_extract_header_empty_text(self):
        result = DocumentParser.extract_header("")
        assert result == ""

    def test_extract_header_with_whitespace(self):
        resume_text = "  John Doe  \n  john@email.com  \n\nExperience"

        result = DocumentParser.extract_header(resume_text)

        assert "John Doe" in result
        assert "john@email.com" in result


class TestDocumentParserRemoveHeader:
    """Test header removal from resume text"""

    def test_remove_header_multiple_lines(self):
        resume_text = "John Doe\njohn@email.com\n\nExperience\nCompany A"

        result = DocumentParser.remove_header(resume_text)

        assert "John Doe" not in result
        assert "john@email.com" not in result
        assert "Experience" in result
        assert "Company A" in result

    def test_remove_header_single_line(self):
        resume_text = "John Doe\nExperience"

        result = DocumentParser.remove_header(resume_text)

        assert "John Doe" not in result
        assert "Experience" in result

    def test_remove_header_empty_text(self):
        result = DocumentParser.remove_header("")
        assert result == ""

    def test_remove_header_preserves_rest(self):
        resume_text = "Name\nContact\nEducation\nExperience\nSkills"

        result = DocumentParser.remove_header(resume_text)

        lines = [line for line in result.split('\n') if line.strip()]
        assert "Name" not in lines
        assert "Contact" not in lines
        assert "Education" in result
        assert "Experience" in result
        assert "Skills" in result


class TestDocumentParserValidateFile:
    """Test file validation"""

    def test_validate_file_exists_and_valid_size(self, tmp_path):
        test_file = tmp_path / "test.pdf"
        test_file.write_text("Small file content")

        result = DocumentParser.validate_file(str(test_file), 10000)

        assert result is True

    def test_validate_file_too_large(self, tmp_path):
        test_file = tmp_path / "large.pdf"
        test_file.write_text("x" * 1000)

        result = DocumentParser.validate_file(str(test_file), 500)

        assert result is False

    def test_validate_file_not_exists(self):
        result = DocumentParser.validate_file("nonexistent.pdf", 10000)

        assert result is False

    def test_validate_file_exact_size(self, tmp_path):
        test_file = tmp_path / "exact.pdf"
        test_file.write_text("x" * 100)

        result = DocumentParser.validate_file(str(test_file), 100)

        assert result is True

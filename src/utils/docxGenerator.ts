import { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel } from 'docx';
import { normalizePersianText } from './persianNormalizer';

export async function generatePersianDocx(title: string, textContent: string): Promise<Blob> {
  const normalizedTitle = normalizePersianText(title);
  const normalizedBody = normalizePersianText(textContent);

  const paragraphs = normalizedBody.split('\n').filter(line => line.trim().length > 0);

  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            margin: {
              top: 1440, // 1 inch
              bottom: 1440,
              left: 1440,
              right: 1440,
            },
          },
        },
        children: [
          new Paragraph({
            heading: HeadingLevel.HEADING_1,
            alignment: AlignmentType.RIGHT,
            bidirectional: true,
            spacing: { before: 240, after: 120 },
            children: [
              new TextRun({
                text: normalizedTitle,
                font: 'Vazirmatn',
                size: 32, // 16pt
                bold: true,
                rightToLeft: true,
              }),
            ],
          }),
          ...paragraphs.map((pText) => {
            const isBullet = pText.startsWith('•') || pText.startsWith('-') || pText.startsWith('*');
            const cleanText = isBullet ? pText.replace(/^[•\-\*]\s*/, '') : pText;

            return new Paragraph({
              alignment: AlignmentType.RIGHT,
              bidirectional: true,
              bullet: isBullet ? { level: 0 } : undefined,
              spacing: { before: 60, after: 100, line: 300 },
              children: [
                new TextRun({
                  text: cleanText,
                  font: 'Vazirmatn',
                  size: 24, // 12pt
                  rightToLeft: true,
                }),
              ],
            });
          }),
        ],
      },
    ],
  });

  return await Packer.toBlob(doc);
}

import { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel, Table, TableRow, TableCell, WidthType, BorderStyle } from 'docx';
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

export async function generatePersianDocxFromBlocks(title: string, blocks: Array<any>): Promise<Blob> {
  const normalizedTitle = normalizePersianText(title);
  const children: any[] = [
    new Paragraph({
      heading: HeadingLevel.HEADING_1,
      alignment: AlignmentType.RIGHT,
      bidirectional: true,
      spacing: { before: 240, after: 160 },
      children: [
        new TextRun({
          text: normalizedTitle,
          font: 'Vazirmatn',
          size: 32,
          bold: true,
          rightToLeft: true,
        }),
      ],
    }),
  ];

  for (const block of blocks) {
    if (block.type === 'heading') {
      const headingLevel = block.level === 2 ? HeadingLevel.HEADING_2 : (block.level === 3 ? HeadingLevel.HEADING_3 : HeadingLevel.HEADING_1);
      const fontSize = block.level === 1 ? 28 : (block.level === 2 ? 26 : 24);
      children.push(
        new Paragraph({
          heading: headingLevel,
          alignment: AlignmentType.RIGHT,
          bidirectional: true,
          spacing: { before: 200, after: 100 },
          children: [
            new TextRun({
              text: normalizePersianText(block.text || ''),
              font: 'Vazirmatn',
              size: fontSize,
              bold: true,
              rightToLeft: true,
            }),
          ],
        })
      );
    } else if (block.type === 'bullet') {
      children.push(
        new Paragraph({
          alignment: AlignmentType.RIGHT,
          bidirectional: true,
          bullet: { level: 0 },
          spacing: { before: 40, after: 60, line: 300 },
          children: [
            new TextRun({
              text: normalizePersianText(block.text || ''),
              font: 'Vazirmatn',
              size: 22,
              rightToLeft: true,
            }),
          ],
        })
      );
    } else if (block.type === 'table' && Array.isArray(block.data)) {
      const rows = block.data.map((row: string[], rIdx: number) => {
        return new TableRow({
          children: row.map((cellText: string) => {
            return new TableCell({
              width: { size: 100 / Math.max(row.length, 1), type: WidthType.PERCENTAGE },
              shading: rIdx === 0 ? { fill: 'F1F5F9' } : undefined,
              children: [
                new Paragraph({
                  alignment: AlignmentType.RIGHT,
                  bidirectional: true,
                  children: [
                    new TextRun({
                      text: normalizePersianText(cellText || ''),
                      font: 'Vazirmatn',
                      size: 20,
                      bold: rIdx === 0,
                      rightToLeft: true,
                    }),
                  ],
                }),
              ],
            });
          }),
        });
      });

      children.push(
        new Table({
          rows,
          width: { size: 100, type: WidthType.PERCENTAGE },
          borders: {
            top: { style: BorderStyle.SINGLE, size: 1, color: 'CBD5E1' },
            bottom: { style: BorderStyle.SINGLE, size: 1, color: 'CBD5E1' },
            left: { style: BorderStyle.SINGLE, size: 1, color: 'CBD5E1' },
            right: { style: BorderStyle.SINGLE, size: 1, color: 'CBD5E1' },
            insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: 'E2E8F0' },
            insideVertical: { style: BorderStyle.SINGLE, size: 1, color: 'E2E8F0' },
          },
        })
      );
    } else {
      children.push(
        new Paragraph({
          alignment: AlignmentType.RIGHT,
          bidirectional: true,
          spacing: { before: 60, after: 100, line: 300 },
          children: [
            new TextRun({
              text: normalizePersianText(block.text || ''),
              font: 'Vazirmatn',
              size: 22,
              rightToLeft: true,
            }),
          ],
        })
      );
    }
  }

  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 },
          },
        },
        children,
      },
    ],
  });

  return await Packer.toBlob(doc);
}

// docx helpers for your-resume-cl-creator
// Encodes the format rules structurally so callers only need to supply content.
// require("docx") directly -- it's preinstalled; do not `npm install` first.
//
// This module is fully anonymous/generic: it has NO hardcoded name, contact info,
// or personal defaults for ANY user. Every identity field (name, phone, email,
// linkedin, website, github) is a REQUIRED argument -- the caller must supply the
// real person's details every time. This is intentional: it stops the skill from
// silently reusing a previous user's identity in someone else's resume/cover letter.

const {
  Document, Packer, Paragraph, TextRun, ExternalHyperlink,
  AlignmentType, BorderStyle, TabStopType,
} = require("docx");

const NAME_SIZE = 32;
const HEAD_SIZE = 20;
const SUB_SIZE = 18;
const BODY_SIZE = 18;
const CL_SIZE = 21;

// BUG FIX (2026-09-20): the `docx` library's TabStopPosition.MAX is a HARDCODED
// constant (9026 twips) computed for the library's own default page margins --
// it does NOT adapt to whatever margins a document actually sets. This resume
// template uses tight custom margins (620 twips/side, see RESUME_MARGIN below)
// to fit more content on one page, so using TabStopPosition.MAX for the
// right-aligned date/location tab stop left a ~1.37in gap before the true right
// margin -- dates/locations looked shifted left instead of flush right against
// the page edge. Fix: compute the right-tab position from THIS document's own
// page width and margins (pageWidth - leftMargin - rightMargin), every time.
// If RESUME_MARGIN or the page width below is ever changed, RESUME_RIGHT_TAB
// must be recomputed the same way -- never swap back to TabStopPosition.MAX.
const RESUME_PAGE_WIDTH = 12240; // Letter width, twips (8.5in)
const RESUME_MARGIN = 620;       // matches the page.margin values in buildResume() below
const RESUME_RIGHT_TAB = RESUME_PAGE_WIDTH - RESUME_MARGIN * 2; // = 11000

function hyperlink(text, url, size = BODY_SIZE) {
  return new ExternalHyperlink({
    link: url,
    children: [new TextRun({ text, style: "Hyperlink", color: "1155CC", underline: {}, size })],
  });
}

function sectionHeading(text) {
  return new Paragraph({
    spacing: { before: 200, after: 80 },
    border: { bottom: { color: "444444", space: 1, style: BorderStyle.SINGLE, size: 6 } },
    children: [new TextRun({ text, bold: true, size: HEAD_SIZE, color: "1F3864" })],
  });
}

function jobHeader(left, right) {
  return new Paragraph({
    spacing: { before: 120, after: 20 },
    tabStops: [{ type: TabStopType.RIGHT, position: RESUME_RIGHT_TAB }],
    children: [
      new TextRun({ text: left, bold: true, size: SUB_SIZE }),
      new TextRun({ text: `\t${right}`, italics: true, size: SUB_SIZE }),
    ],
  });
}

function subHeader(left, right) {
  return new Paragraph({
    spacing: { after: 40 },
    tabStops: [{ type: TabStopType.RIGHT, position: RESUME_RIGHT_TAB }],
    children: [
      new TextRun({ text: left, italics: true, size: BODY_SIZE }),
      new TextRun({ text: `\t${right}`, italics: true, size: BODY_SIZE }),
    ],
  });
}

function bullet(text) {
  return new Paragraph({
    bullet: { level: 0 },
    spacing: { after: 40 },
    children: [new TextRun({ text, size: BODY_SIZE })],
  });
}

function skillLine(label, value) {
  return new Paragraph({
    spacing: { after: 30 },
    children: [
      new TextRun({ text: `${label}: `, bold: true, size: BODY_SIZE }),
      new TextRun({ text: value, size: BODY_SIZE }),
    ],
  });
}

function requireField(obj, field, fnName) {
  if (!obj[field] || (typeof obj[field] === "string" && !obj[field].trim())) {
    throw new Error(
      `${fnName}: \`${field}\` is required. This module never defaults to a previous user's identity -- ` +
      `supply this specific applicant's real ${field} (use a bracketed placeholder like "[Your ${field}]" only if the real value is genuinely unknown yet).`
    );
  }
}

/**
 * buildResume({
 *   filename,
 *   name, phone, email, linkedin, github, website,   // ALL REQUIRED -- this applicant's real identity/contact info
 *   summary,                              // REQUIRED: 2-3 sentence string, tailored per role
 *   education: [{ school, location, line, dates }],
 *   experience: [{ title, dates, org, location, bullets: [] }],
 *   experienceSectionTitle,               // optional override, e.g. "Relevant Experience — <domain>"
 *   projects: { sectionTitle, items: [] },
 *   skills: [{ label, value }],
 *   publications: [],                     // optional -- omit or [] if not used
 *   extraSections: [{ title, items: [] }] // optional -- any other optional section
 * })
 */
function buildResume({
  filename, name, phone, email, linkedin, github, website,
  summary, education, experience, experienceSectionTitle,
  projects, skills, publications = [], extraSections = [],
}) {
  const identity = { name, phone, email, linkedin, github, website };
  for (const field of Object.keys(identity)) requireField(identity, field, "buildResume");
  requireField({ summary }, "summary", "buildResume");

  const children = [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 40 },
      children: [new TextRun({ text: name, bold: true, size: NAME_SIZE })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 120 },
      children: [
        new TextRun({ text: `${phone} | ${email} | `, size: BODY_SIZE }),
        hyperlink("LinkedIn", linkedin),
        new TextRun({ text: " | ", size: BODY_SIZE }),
        hyperlink("GitHub", github),
        new TextRun({ text: " | ", size: BODY_SIZE }),
        hyperlink("Personal Website", website),
      ],
    }),
    new Paragraph({
      spacing: { after: 160 },
      children: [new TextRun({ text: summary, size: BODY_SIZE, italics: true })],
    }),
    sectionHeading("Education"),
  ];

  for (const e of education) {
    children.push(jobHeader(e.school, e.location));
    children.push(subHeader(e.line, e.dates));
  }

  children.push(sectionHeading(experienceSectionTitle || "Experience"));
  for (const job of experience) {
    children.push(jobHeader(job.title, job.dates));
    children.push(subHeader(job.org, job.location));
    for (const b of job.bullets) children.push(bullet(b));
  }

  children.push(sectionHeading(projects.sectionTitle || "Projects"));
  for (const p of projects.items) children.push(bullet(p));

  children.push(sectionHeading("Technical Skills"));
  for (const s of skills) children.push(skillLine(s.label, s.value));

  if (publications.length) {
    children.push(sectionHeading("Selected Publications"));
    for (const p of publications) children.push(bullet(p));
  }

  for (const section of extraSections) {
    children.push(sectionHeading(section.title));
    for (const item of section.items) children.push(bullet(item));
  }

  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            // NOTE: width and left/right margins here MUST stay in sync with
            // RESUME_PAGE_WIDTH / RESUME_MARGIN above -- those feed RESUME_RIGHT_TAB,
            // the right-aligned tab stop used by jobHeader()/subHeader() for the
            // date/location columns. Changing margins without updating that constant
            // reintroduces the "dates not right-aligned" bug fixed on 2026-09-20.
            size: { width: RESUME_PAGE_WIDTH, height: 15840 },
            margin: { top: RESUME_MARGIN, bottom: RESUME_MARGIN, left: RESUME_MARGIN, right: RESUME_MARGIN },
          },
        },
        children,
      },
    ],
  });

  return Packer.toBuffer(doc).then((buf) => {
    require("fs").writeFileSync(filename, buf);
    console.log("written:", filename);
  });
}

function clPara(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 200, line: 300 },
    children: [new TextRun({ text, size: CL_SIZE, ...opts })],
  });
}

/**
 * buildCoverLetter({
 *   filename,
 *   name, phone, email, linkedin, github, website,   // ALL REQUIRED -- this applicant's real identity/contact info
 *   // CHANGED 2026-09-20 (user request): GitHub is now included in the cover letter header,
 *   // matching the resume's header. Previously GitHub was resume-only "by design" -- that
 *   // exclusion is retired; every identity link that appears on the resume now also appears
 *   // on the cover letter. Do not silently drop GitHub from the header again.
 *   date,
 *   companyLines: ["Hiring Team", "Company Name", "Street", "City, State ZIP, Country"],
 *   positionTitle,                 // e.g. "Control Engineer for Actuators and Sensors" -- Re: line is built from this
 *   paragraphs: [intro, expertise, application, closing]   // REQUIRED: exactly 4 strings
 * })
 */
function buildCoverLetter({
  filename, name, phone, email, linkedin, github, website,
  date, companyLines, positionTitle, paragraphs,
}) {
  const identity = { name, phone, email, linkedin, github, website };
  for (const field of Object.keys(identity)) requireField(identity, field, "buildCoverLetter");
  if (!Array.isArray(paragraphs) || paragraphs.length !== 4) {
    throw new Error("buildCoverLetter: `paragraphs` must be an array of exactly 4 strings (intro, expertise, application, closing).");
  }
  if (!positionTitle) {
    throw new Error("buildCoverLetter: `positionTitle` is required to build the bold Re: line.");
  }
  if (!Array.isArray(companyLines) || companyLines.length < 2) {
    throw new Error("buildCoverLetter: `companyLines` is required -- at least [\"Hiring Team\", \"Company Name\"], ideally with the full mailing address on subsequent lines.");
  }
  if (!date) {
    throw new Error("buildCoverLetter: `date` is required (use today's date).");
  }

  const children = [
    new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: name, bold: true, size: CL_SIZE })] }),
    new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: `${phone} | ${email}`, size: CL_SIZE })] }),
    new Paragraph({
      spacing: { after: 240 },
      children: [
        hyperlink("LinkedIn", linkedin, CL_SIZE),
        new TextRun({ text: " | ", size: CL_SIZE }),
        hyperlink("GitHub", github, CL_SIZE),
        new TextRun({ text: " | ", size: CL_SIZE }),
        hyperlink("Personal Website", website, CL_SIZE),
      ],
    }),
    new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: date, size: CL_SIZE })] }),
    new Paragraph({ spacing: { after: 240 } }),
  ];

  companyLines.forEach((line, i) => {
    children.push(new Paragraph({
      spacing: { after: i === companyLines.length - 1 ? 240 : 0 },
      children: [new TextRun({ text: line, size: CL_SIZE, bold: i === 0 })],
    }));
  });

  children.push(new Paragraph({
    spacing: { after: 240 },
    children: [new TextRun({ text: `Re: Application for ${positionTitle}`, size: CL_SIZE, bold: true })],
  }));
  children.push(clPara("Dear Hiring Team,"));
  for (const p of paragraphs) children.push(clPara(p));
  children.push(new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: "Sincerely,", size: CL_SIZE })] }));
  children.push(new Paragraph({ spacing: { after: 0 }, children: [new TextRun({ text: name, size: CL_SIZE, bold: true })] }));

  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            size: { width: 12240, height: 15840 },
            margin: { top: 900, bottom: 900, left: 1080, right: 1080 },
          },
        },
        children,
      },
    ],
  });

  return Packer.toBuffer(doc).then((buf) => {
    require("fs").writeFileSync(filename, buf);
    console.log("written:", filename);
  });
}

module.exports = { buildResume, buildCoverLetter };

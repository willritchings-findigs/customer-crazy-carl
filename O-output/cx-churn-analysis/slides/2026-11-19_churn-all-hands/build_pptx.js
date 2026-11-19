// Builds the corrected churn all-hands slides as a .pptx mirroring the HTML deck frames.
// Canvas: 1240 x 697.5 px -> 13.333 x 7.5 in (1 px = 0.010753 in). Fonts named per the
// Findigs deck PPTX law: no embedding; recipients without the brand fonts see fallbacks.
const pptxgen = require('pptxgenjs');
const { applyTheme } = require(process.argv[3]);
const OUT = process.argv[2];

const PX = 13.333 / 1240;           // inches per canvas px
const pt = (px) => Math.round(px * 0.7742 * 2) / 2;

// Token colors. Muted and hairline are the ink-at-alpha tokens composited on cream
// (ink 0.64 and 0.12 over cream), since PPTX text cannot carry alpha.
const THEME = {
  name: 'Findigs deck canon v3',
  headFontFace: 'Orbikular',
  bodyFontFace: 'Findigs Sans',
  colors: {
    dk1: '212B14', lt1: 'FAF9F6', dk2: '6F7565', lt2: 'E0E0DB',
    accent1: '8EDE65', accent2: '3F7A1E', accent3: 'CFEEBA', accent4: '163436', accent5: 'B45309', accent6: 'B91C1C',
    hlink: '3F7A1E', folHlink: '3F7A1E',
  },
};

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = 'Churn update, all-hands (Nov 2026)';
const C = pres.SchemeColor;
const M = 72 * PX;                   // 72 px side margin
const W = 13.333 - 2 * M;

pres.defineSlideMaster({
  title: 'Findigs content',
  background: { color: THEME.colors.lt1 },
  objects: [
    { placeholder: { options: { name: 'eyebrow', type: 'body', x: M, y: 64 * PX, w: 8, h: 0.3, margin: 0, fontSize: pt(13), bold: true, color: C.text2, charSpacing: 2.5, fontFace: THEME.bodyFontFace }, text: 'Eyebrow' } },
    { placeholder: { options: { name: 'title', type: 'title', x: M, y: 92 * PX, w: 820 * PX, h: 0.7, margin: 0, fontSize: pt(34), color: C.text1, fontFace: THEME.headFontFace, valign: 'top', align: 'left' }, text: 'Headline.' } },
    { text: { text: 'Findigs', options: { x: M, y: 7.5 - 0.52, w: 2, h: 0.3, margin: 0, fontSize: pt(11), color: C.text2, isTextBox: true } } },
  ],
  slideNumber: { x: 13.333 - M - 1, y: 7.5 - 0.52, w: 1, h: 0.3, margin: 0, fontSize: pt(11), color: C.text2, align: 'right' },
});

pres.addSection({ title: 'Churn update' });
const body = (slide, text, opts) => slide.addText(text, { isTextBox: true, margin: 0, color: C.text1, ...opts });
const hairline = (slide, x, y, w) => slide.addShape(pres.ShapeType.line, { x, y, w, h: 0, line: { color: THEME.colors.lt2, width: 0.75 } });

// ---- Slide 1: Big-stat trio (archetype 054)
{
  const s = pres.addSlide({ masterName: 'Findigs content', sectionTitle: 'Churn update' });
  s.addText('CHURN UPDATE', { placeholder: 'eyebrow' });
  s.addText('Churn so far this year, and what is coming.', { placeholder: 'title' });
  const stats = [
    ['$4.26M', 'True churn YTD', 'Failure to launch excluded. Findigs Hub churn dashboard, Nov 18.'],
    ['$0.89M', 'Failure to launch YTD', '19 accounts that never went live. Findigs Hub churn dashboard, Nov 18.'],
    ['$1.47M', 'Q4 churn to date', 'HubSpot churned flag, Nov 18: Harbor Group $1.28M, Weiss $97K, McCaw $80K, Chroma $7K. Dashboard sync pending for the first two.'],
  ];
  const gx = M, gy = 280 * PX, cw = (1096 * PX) / 3, ch = 225 * PX;
  stats.forEach(([v, l, src], i) => {
    const x = gx + i * cw;
    s.addShape(pres.ShapeType.rect, { x, y: gy, w: cw, h: ch, fill: { type: 'none' }, line: { color: THEME.colors.lt2, width: 0.75 } });
    body(s, v, { x: x + 32 * PX, y: gy + 30 * PX, w: cw - 64 * PX, h: 0.9, fontSize: pt(72), bold: true, fontFace: THEME.bodyFontFace, charSpacing: -1.5 });
    body(s, l, { x: x + 32 * PX, y: gy + 118 * PX, w: cw - 64 * PX, h: 0.3, fontSize: pt(15), bold: true });
    body(s, src, { x: x + 32 * PX, y: gy + 148 * PX, w: cw - 64 * PX, h: 0.7, fontSize: pt(13), color: C.text2, valign: 'top' });
  });
  s.addNotes('True churn YTD is unchanged from the Nov 16 run. The Q4 tile is the correction: HubSpot flagged Harbor Group (Nov 5), Weiss (Nov 4) and McCaw (Nov 16) as churned; only Chroma is on the dashboard so far because the other three fail the taxonomy or status checks. Say that out loud so nobody reads the dashboard\'s $6.6K as the Q4 answer.');
}

// ---- Slide 2: Section summary (archetype 024)
{
  const s = pres.addSlide({ masterName: 'Findigs content', sectionTitle: 'Churn update' });
  s.addText('CHURN UPDATE', { placeholder: 'eyebrow' });
  s.addText('Why Evernest left.', { placeholder: 'title' });
  const rows = [
    ['Moving the full portfolio to Boom.', 'Off Findigs in December. $428,400 ACV lands in Q4 churn when the date holds. CS debrief, Oct 30.'],
    ['Configurability was the number one stated reason.', 'The first reason given in the exit conversation. CS debrief, Oct 30.'],
    ['Three account managers in one year, though the latest relationship was strong.', 'HubSpot still shows a 2025 Merged/Acquired churn flag; CS to correct date and reason. HubSpot, Nov 18.'],
  ];
  const rw = 960 * PX, rh = 92 * PX, y0 = 176 * PX;
  rows.forEach(([b, sup], i) => {
    const y = y0 + i * rh;
    hairline(s, M, y, rw);
    s.addShape(pres.ShapeType.ellipse, { x: M, y: y + 28 * PX, w: 16 * PX, h: 16 * PX, fill: { color: THEME.colors.accent1 }, line: { color: THEME.colors.accent1, width: 0 } });
    s.addText('✓', { x: M, y: y + 28 * PX, w: 16 * PX, h: 16 * PX, margin: 0, fontSize: 7, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle', isTextBox: true });
    body(s, b, { x: M + 44 * PX, y: y + 22 * PX, w: rw - 44 * PX, h: 0.32, fontSize: pt(18), bold: true });
    body(s, sup, { x: M + 44 * PX, y: y + 52 * PX, w: rw - 44 * PX, h: 0.32, fontSize: pt(14), color: C.text2 });
  });
  hairline(s, M, y0 + rows.length * rh, rw);
  s.addNotes('Evernest is $428,400 of ACV and still shows At Risk on the dashboard. HubSpot carries a stale churn flag from September 2025 with reason Merged/Acquired, which contradicts this story. CS should set the December date and a taxonomy reason so it lands in Q4 correctly.');
}

// ---- Slide 3: Table, small density (archetype 078)
{
  const s = pres.addSlide({ masterName: 'Findigs content', sectionTitle: 'Churn update' });
  s.addText('CHURN UPDATE', { placeholder: 'eyebrow' });
  s.addText('SMB accounts on notice.', { placeholder: 'title' });
  const tw = 1040 * PX;
  const colW = [0.24, 0.44, 0.32].map((f) => f * tw);
  const cellBorder = () => [{ type: 'none' }, { type: 'none' }, { type: 'solid', pt: 0.75, color: THEME.colors.lt2 }, { type: 'none' }];
  const th = (t) => ({ text: t, options: { fontSize: pt(11), bold: true, color: THEME.colors.dk2, charSpacing: 1.5, border: cellBorder(), margin: [0.16, 0.17, 0.16, 0.17] } });
  const td = (t, boldCell) => ({ text: t, options: { fontSize: pt(16), bold: !!boldCell, color: boldCell ? THEME.colors.dk1 : THEME.colors.dk2, border: cellBorder(), margin: [0.2, 0.17, 0.2, 0.17], valign: 'middle' } });
  const data = [
    [th('ACCOUNT, UNITS, PLATFORM'), th('WHY, PER THE NOV 12 CS CHECK-IN'), th('CLOSED WON ACV, HUBSPOT, AND TIMING')],
    [td('FBM, 1,200, AppFolio', true), td('Consolidating tech stack; income verification friction'), td('$70K, losing at end of year')],
    [td('Cobalt, 800, Buildium', true), td('Team works inside applications; many Buildium issues'), td('$55K, losing at renewal')],
    [td('Red Bricks, 400, Rentvine', true), td('No two-way integration; likely going native or to Boom'), td('$27K, likely loss')],
  ];
  s.addTable(data, { x: M, y: 275 * PX, w: tw, colW, rowH: [0.5, 0.78, 0.78, 0.78], fontFace: THEME.bodyFontFace, fill: { type: 'none' } });
  s.addNotes('All three are Live in HubSpot and Yellow in Client Health, so none show as At Risk on the dashboard yet. ACV is HubSpot Closed Won; the notice status is what CS heard at the Nov 12 churn check-in. Red Bricks corrected from 500 units and $35K to 400 units and $27K.');
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log('wrote', OUT);
})();

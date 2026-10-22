"""Render synchronized English and Chinese findings, figures and standalone PDFs."""
import sys,json,re,math,shutil,hashlib,argparse,subprocess,tempfile
from pathlib import Path
import numpy as np
from pypdf import PdfReader,PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor,black,white
R=Path(__file__).resolve().parent; ROOT=R.parent
parser=argparse.ArgumentParser();parser.add_argument('--data-root',type=Path,default=ROOT/'data');parser.add_argument('--lang',choices=['en','zh'],default='en');parser.add_argument('--cjk-font',type=Path,default=Path('/System/Library/Fonts/Supplemental/Songti.ttc'));parser.add_argument('--cjk-index',type=int,default=6);args=parser.parse_args()
import report_layout as b
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import black
LANG=args.lang;OUT=ROOT/'docs/pdf'/('the-shape-of-song-ci-'+LANG+'.pdf');OUT.parent.mkdir(parents=True,exist_ok=True)
a=json.loads((args.data_root/'atlas.json').read_text());e=json.loads((R/'results/semantic-findings.json').read_text());docs=a['documents'];co=np.array(a['coordinates']['tsne'])
pdfmetrics.registerFont(TTFont('Chinese',str(args.cjk_font),subfontIndex=args.cjk_index))
translations=json.loads((R/'translations.zh.json').read_text());tr=lambda s:translations.get(s,s) if LANG=='zh' else s
b.S=[];md=[];figure_count=0
if LANG=='zh':
 for st in b.styles.values():st.fontName='Chinese';st.wordWrap='CJK'
oldtext=b.text
def localized_text(t,x,y,size=9,bold=False):
 t=tr(t)
 if LANG=='zh' and re.search(r'[\u2e80-\u9fff]',t):
  b.C.setFont('Chinese',size);b.C.setFillColor(black);b.C.drawString(x,b.H-y-size,b.clean(t))
 else:oldtext(t,x,y,size,bold)
b.text=localized_text
def add(s,style='body'):
 md.append((('# ' if not md else '## ') if style=='title' else '### ' if style=='heading' else '')+tr(s)+'\n');s=tr(s)
 s=b.escape(b.clean(s));s=re.sub(r'([\u2e80-\u9fff\uf900-\ufaff\uff00-\uffef·]+)',r'<font name="Chinese">\1</font>',s)
 b.S.append(Paragraph(s.replace('\n','<br/>'),b.styles[style]))
def page(t):
 if b.S:b.S.append(b.PageBreak())
 add(t,'title')
colors=['#ac623d','#7c7199','#21776d','#a58743','#438e9b']
def map_panel(view,x,y,w,h,regions=False,highlight=None):
 pts=np.array(a['coordinates'][view]);lo=pts.min(0);hi=pts.max(0);pad=(hi-lo)*.10;lo-=pad;hi+=pad
 xx=lambda v:x+(v-lo[0])/(hi[0]-lo[0])*w; yy=lambda v:y+h-(v-lo[1])/(hi[1]-lo[1])*h
 for gx in np.linspace(lo[0],hi[0],5):b.line([(xx(gx),y),(xx(gx),y+h)],.9,.4)
 for gy in np.linspace(lo[1],hi[1],5):b.line([(x,yy(gy)),(x+w,yy(gy))],.9,.4)
 order=sorted(range(len(docs)),key=lambda i:docs[i]['label']==highlight) if highlight else range(len(docs))
 for i in order:
  d=docs[i]
  col='#b0bcb3' if regions else {'豪放派':'#b76c4e','婉约派':'#438e9b'}.get(d['label'],'#b0bcb3')
  if highlight:col={'豪放派':'#b76c4e','婉约派':'#438e9b'}[highlight] if d['label']==highlight else '#dce1dc'
  b.C.setFillColor(HexColor(col));b.C.circle(xx(pts[i,0]),b.H-yy(pts[i,1]),2.5 if not highlight or d['label']==highlight else 1.9,stroke=0,fill=1)
 if regions:
  for j,r in enumerate(e['regions']):
   for i in r['indices']:
    b.C.setStrokeColor(HexColor(colors[j]));b.C.setLineWidth(1);b.C.circle(xx(pts[i,0]),b.H-yy(pts[i,1]),3.7,stroke=1,fill=0)
   cx,cy=r['center'];b.C.setFillColor(HexColor(colors[j]));b.C.circle(xx(cx),b.H-yy(cy),8,fill=1,stroke=0)
   b.C.setFillColor(white);b.C.setFont('Bold',8);b.C.drawCentredString(xx(cx),b.H-yy(cy)-2.8,str(j+1))
 title='t-SNE' if view=='tsne' else 'UMAP'
 if highlight:title+=' / '+('Haofang (33)' if highlight=='豪放派' else 'Wanyue (55)')
 b.text(title,x,y-21,10,True)
def export_plot(height,fn,stem):
 b.plot(height,fn)
 figdir=ROOT/'docs/figures';figdir.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='song-ci-figure-') as d:
  pdf=Path(d)/'figure.pdf';c=Canvas(str(pdf),pagesize=(b.CW,height));b.C=c;c.translate(0,height-b.H);fn();c.showPage();c.save()
  dest=figdir/(stem+'-'+LANG)
  subprocess.run(['pdftoppm','-singlefile','-scale-to','1800','-png',str(pdf),str(dest)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 md.append('!['+tr(stem)+'](figures/'+stem+'-'+LANG+'.png)\n')
page('The shape of Song Ci')
add('Can semantic maps reveal how Song Ci poems relate through style, imagery and emotion? This analysis combines fixed visualizations, original-vector comparisons and close reading.')
add('Song Ci is a traditional Chinese lyric-poetry form, originally written to tune patterns. Its two major stylistic traditions are Haofang (豪放派), known for expansive, heroic expression, and Wanyue (婉约派), known for intimate, delicate expression.')
add('Question: If each poem becomes a natural-language embedding in a vector database, will a nonlinear 2D map naturally separate the two schools? Will poems sharing imagery or emotion gather into nearby “islands”?','idea')
add('Audience: readers exploring Chinese poetry through semantic search. Data: 240 anthology entries and 96 canonical authors from Guwendao, captured October 20, 2026. Complete verse alone enters Qwen3-Embedding-4B: 2,560 dimensions, L2-normalized, stored in Supabase. Titles, poets and school labels are excluded from fitting.','small')
def schools():
 for row,view in enumerate(['tsne','umap']):
  for col,school in enumerate(['豪放派','婉约派']):
   map_panel(view,col*266,24+row*153,245,126,highlight=school)
 b.text('Color: selected school   Pale gray: all other poems   Coordinates fixed within each method',0,313,8)
export_plot(335,schools,'01-school-separation')
add('The maps show overlapping school tendencies. Eight representative poets supply 33 Haofang and 55 Wanyue labels; 152 poems remain unlabeled. The original-vector silhouette is 0.094, reflecting substantial overlap.','small')
add('School labels summarize a poet’s predominant style, and individual works often span styles: Haofang representative 苏轼 wrote the intimate, Wanyue-like elegy《江城子·乙卯正月二十日夜记梦》in memory of his wife.','small')
add('Among each poem’s five nearest labeled works by other authors, 61.4% share its school. Reassigning two of the eight authors to Haofang gives a 57.1% average; 8 of 28 assignments reach or exceed the observed value.','small')
page('Where themes gather')
add('Big idea: the map brings shared imagery and emotion into view. Frontier/history and chamber longing have the strongest similarity among the five regions examined.','idea')
def regions():
 map_panel('tsne',8,22,495,285,True)
export_plot(326,regions,'02-thematic-islands')
add('Each region contains the eight nearest t-SNE points to a manually selected center. Rings mark these works. The table compares their original-vector cosine similarity, including pairs by different authors.','small')
rows=[['Region / location','Mean cosine','Other-author\npairs only']]
for j,r in enumerate(e['regions']):rows.append([f"{j+1}. {r['name']}",f"{r['mean_cosine']:.3f}",f"{r['cross_author_cosine']:.3f}"])
rows.append(['All 240 poems (pair average)',f"{e['pair_baseline']:.3f}",f"{e['cross_author_baseline']:.3f}"])
rows=[[tr(v) for v in row] for row in rows]
if LANG=='zh':
 oldfont=b.styles['body'].fontName
 # Table uses a CJK font in the Chinese edition.
 cs=ParagraphStyle('cellzh',fontName='Chinese',fontSize=9,leading=12,wordWrap='CJK')
 table=b.Table([[Paragraph(b.escape(v).replace('\n','<br/>'),cs) for v in row] for row in rows],colWidths=[b.CW-178,83,95])
 table.setStyle(b.TableStyle([('BACKGROUND',(0,0),(-1,0),b.Color(.92,.92,.92)),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.4,b.Color(.75,.75,.75)),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]));b.S.extend([table,Spacer(1,12)])
else:b.tab(rows,[b.CW-178,83,95],9)
md.append('\n'.join('| '+' | '.join(row).replace('\n',' ')+' |' for row in [rows[0],['---']*3,*rows[1:]]))
add('Frontier/history, chamber longing, pastoral life and parting exceed the corpus pair average. Life reflection has a cross-author similarity of 0.592, below the 0.623 baseline, and combines a wider range of emotions.','small')
page('Read the islands')
# Original-language evidence, with concise English interpretation.
cards=[
('1. Frontier & historical memory | lower left','辛弃疾《永遇乐·京口北固亭怀古》：千古江山，英雄无觅，孙仲谋处。','张孝祥《水调歌头·和庞佑父》：湖海平生豪气，关塞如今风景，剪烛看吴钩。','Historical heroes, lost territory and martial imagery connect works by five authors.'),
('2. Life reflection | bottom','苏轼《定风波·莫听穿林打叶声》：一蓑烟雨任平生。','苏轼《江城子·乙卯正月二十日夜记梦》：十年生死两茫茫，不思量，自难忘。','Resilience and bereavement sit nearby. Five of the eight works are by 苏轼, whose writing connects several emotions in this region.'),
('3. Pastoral life | lower right','辛弃疾《西江月·夜行黄沙道中》：稻花香里说丰年，听取蛙声一片。','秦观《行香子·树绕村庄》：树绕村庄，水满陂塘。','Fields, villages, crops and rural sounds recur across seven authors. A Haofang poet and a Wanyue poet meet through shared imagery.'),
('4. Parting & remembrance | right','柳永《雨霖铃·寒蝉凄切》：执手相看泪眼，竟无语凝噎。','欧阳修《浪淘沙·把酒祝东风》：聚散苦匆匆，此恨无穷。','Farewell, absent companions and returning seasons link these works. Remembered loss also appears in 晏殊’s nearby poem about falling flowers.'),
('5. Chamber longing | upper right','李清照《一剪梅·红藕香残玉簟秋》：一种相思，两处闲愁。','唐琬《钗头凤·世情薄》：欲笺心事，独语斜阑。','Intimate longing and enclosed spaces recur. Six of eight works are by 李清照, alongside 唐琬 and 陆游; cross-author similarity is 0.707.')]
for title,q1,q2,interpret in cards:
 add(title,'heading');add(q1+'\n'+q2,'small');add(interpret,'small')
add('Conclusion: the maps show overlapping schools and recognizable thematic neighborhoods. Original-vector neighbors help readers explore these connections through close reading. Next, use independent theme labels and a second anthology to evaluate the regions selected here.','small')
add('Source anthology: Guwendao, 宋词三百首. School background: Li, Li & Guan, Art Appreciation (2nd ed.), Tsinghua University Press, 2018, p. 37.','small')
for label,url in [('GitHub - code and data','https://github.com/yihan2588/the-shape-of-song-ci'),('Vercel - interactive app','https://song-ci-atlas.vercel.app')]:
 b.S.append(Paragraph(f'<b>{tr(label)}:</b> <link href="{url}" color="black">{url}</link>',b.styles['small']))
def footer(c,doc):
 c.setFont('Body',8);c.setFillGray(0);c.drawRightString(b.W-b.M,22,str(doc.page))
SimpleDocTemplate(str(OUT),pagesize=b.A4,leftMargin=b.M,rightMargin=b.M,topMargin=44,bottomMargin=38,title=tr('The shape of Song Ci'),author='Yihan Wu').build(b.S,onFirstPage=footer,onLaterPages=footer)
md.extend(['[GitHub](https://github.com/yihan2588/the-shape-of-song-ci) · [Live app](https://song-ci-atlas.vercel.app)','',tr('Reproduce: `python analysis/semantic_findings.py`, then `python analysis/render_findings.py --lang en` and `--lang zh`. Saved coordinates and vectors are reused; the app is unchanged.')])
mdpath=ROOT/'docs'/('FINDINGS.md' if LANG=='en' else 'FINDINGS.zh.md')
md.insert(1,'[English](FINDINGS.md) · [中文](FINDINGS.zh.md)')
mdpath.write_text('\n\n'.join(v.strip() for v in md)+'\n')
print(OUT)

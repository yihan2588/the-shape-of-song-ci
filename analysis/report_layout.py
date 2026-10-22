"""Shared portrait report layout with monochrome text and colored vector figures."""
import csv,json,math,bisect,re,textwrap
from pathlib import Path
from xml.sax.saxutils import escape
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color,HexColor,black,white
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Flowable,Table,TableStyle,KeepTogether,Preformatted
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
ROOT=Path(__file__).resolve().parent

W,H=A4;M=42;CW=W-2*M
TEAL="#21776d";RUST="#ac623d";INK="#143b37"
ASSET_COLORS={"NVDA":TEAL,"TSLA":RUST,"SPY":"#697796"}
for name,path in [('Body','Arial.ttf'),('Bold','Arial Bold.ttf'),('Title','Georgia.ttf'),('Code','Courier New.ttf')]:
 fp=Path('/System/Library/Fonts/Supplemental')/path
 if fp.exists():pdfmetrics.registerFont(TTFont(name,str(fp)))
 else:pdfmetrics.registerFont(pdfmetrics.Font(name,{'Body':'Helvetica','Bold':'Helvetica-Bold','Title':'Times-Roman','Code':'Courier'}[name],'WinAnsiEncoding'))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Body',boldItalic='Bold')
styles={
 'body':ParagraphStyle('body',fontName='Body',fontSize=10.5,leading=15,spaceAfter=10),
 'small':ParagraphStyle('small',fontName='Body',fontSize=9,leading=12.5,spaceAfter=9),
 'title':ParagraphStyle('title',fontName='Title',fontSize=24,leading=29,spaceAfter=14),
 'heading':ParagraphStyle('heading',fontName='Bold',fontSize=12,leading=16,spaceBefore=6,spaceAfter=8),
 'idea':ParagraphStyle('idea',fontName='Bold',fontSize=10.8,leading=15,spaceAfter=12),
 'code':ParagraphStyle('code',fontName='Code',fontSize=7.8,leading=9.4,spaceAfter=10),
}
S=[];C=None

def clean(t):return str(t).replace('–','-').replace('—',' - ').replace('\u2011','-')
def p(t,style='body'):return Paragraph(escape(clean(t)).replace('\n','<br/>'),styles[style])
def add(t,style='body'):S.append(p(t,style))
def page(title):
 if S:S.append(PageBreak())
 add(title,'title')
def text(t,x,y,size=9,bold=False):
 C.setFont('Bold' if bold else 'Body',size);C.setFillColor(black);C.drawString(x,H-y-size,clean(t))
def right(t,x,y,size=8):
 C.setFont('Body',size);C.setFillColor(black);C.drawRightString(x,H-y-size,clean(t))
def line(points,gray=0,width=1,dash=None):
 if not points:return
 C.saveState()
 if isinstance(gray,str):C.setStrokeColor(HexColor(gray))
 else:C.setStrokeGray(gray)
 C.setLineWidth(width)
 if dash:C.setDash(*dash)
 path=C.beginPath();path.moveTo(points[0][0],H-points[0][1])
 for x,y in points[1:]:path.lineTo(x,H-y)
 C.drawPath(path);C.restoreState()
def grid(x,y,w,h,xmin,xmax,ymin,ymax,xticks,yticks,xlabel='',ylabel=''):
 xx=lambda v:x+(v-xmin)/(xmax-xmin)*w;yy=lambda v:y+h-(v-ymin)/(ymax-ymin)*h
 if ylabel:text(ylabel,x,y-17,8.5)
 for v in yticks:
  line([(x,yy(v)),(x+w,yy(v))],.86,.45);right(f'{v:g}',x-6,yy(v)-4,8)
 for v,label in xticks:
  text(label,xx(v)-pdfmetrics.stringWidth(str(label),'Body',8)/2,y+h+6,8)
 line([(x,y),(x,y+h),(x+w,y+h)],.4,.6)
 if xlabel:text(xlabel,x+w/2-pdfmetrics.stringWidth(xlabel,'Body',8)/2,y+h+23,8)
 return xx,yy
class Plot(Flowable):
 def __init__(self,height,fn):Flowable.__init__(self);self.width=CW;self.height=height;self.fn=fn
 def draw(self):
  global C
  C=self.canv;C.saveState();C.translate(0,self.height-H);self.fn();C.restoreState()
def plot(h,fn):S.append(Plot(h,fn));S.append(Spacer(1,10))
def hist(vals,n,title,maxy=None,height=180):
 def draw():
  text(title,0,0,11,True);lo,hi=min(vals),max(vals);bounds=[lo+(hi-lo)*i/n for i in range(1,n)];counts=[0]*n
  for v in vals:counts[bisect.bisect_right(bounds,v)]+=1
  top=maxy or math.ceil(max(counts)/100)*100
  xx,yy=grid(40,39,CW-51,height-86,lo,hi,0,top,[(lo+(hi-lo)*i/4,f'{lo+(hi-lo)*i/4:.1f}') for i in range(5)],[0,top/2,top],title.split(' / ')[0]+' (source units)','Number of days')
  C.setFillColor(HexColor(TEAL))
  for i,count in enumerate(counts):
   a=lo+(hi-lo)*i/n;b=lo+(hi-lo)*(i+1)/n
   C.rect(xx(a)+.35,H-yy(0),xx(b)-xx(a)-.7,yy(0)-yy(count),fill=1,stroke=0)
 plot(height,draw)

def code(label,path,ranges,size=7.8):
 add(label,'heading');lines=path.read_text().splitlines();out=[]
 maxchars=int(CW/(size*.6))
 for j,(a,b) in enumerate(ranges):
  if j:out.append('...')
  for ln in lines[a-1:b]:
   indent=min(len(ln)-len(ln.lstrip())+2,12)
   out.extend(textwrap.wrap(clean(ln),maxchars,subsequent_indent=' '*indent,replace_whitespace=False,drop_whitespace=False,break_long_words=True,break_on_hyphens=False) or [''])
 st=ParagraphStyle('codeblock',parent=styles['code'],fontSize=size,leading=size*1.21)
 S.append(Preformatted('\n'.join(out),st))

def tab(rows,widths,fs=9):
 cs=ParagraphStyle('cell',fontName='Body',fontSize=fs,leading=fs*1.35)
 rr=[[Paragraph(escape(clean(v)).replace('\n','<br/>'),cs) for v in row] for row in rows]
 t=Table(rr,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),Color(.92,.92,.92)),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.4,Color(.75,.75,.75)),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]));S.append(t);S.append(Spacer(1,12))
def brief(story):
 add('Audience: '+story['audience'],'small');add('Question: '+story['question'],'small');add(story['big_idea'],'idea')

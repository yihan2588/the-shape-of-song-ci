import os
os.environ['MPLCONFIGDIR']=os.path.join(os.path.dirname(__file__),'../.cache/matplotlib')
import json,numpy as np
from pathlib import Path
APP=Path(__file__).resolve().parents[1]
RESULTS=APP/'analysis/results'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
from matplotlib import font_manager as fm
OUT=APP/'docs/figures'
ROOT=APP/'data'
coords=json.loads((ROOT/'derived/coordinates.json').read_text());labs=np.load(RESULTS/'song-cluster-labels.npz');validation=json.load(open(RESULTS/'song-cluster-validation.json'))
PAPER='#faf8f2';INK='#26332f';MUTED='#69736d';GRAY='#c8cbc4';TEAL='#297e81';RUST='#b65d40';PURPLE='#8663a4'
plt.rcParams.update({'font.family':['DejaVu Sans','Arial Unicode MS'],'font.size':12,'text.color':INK,'axes.labelcolor':MUTED,'xtick.color':MUTED,'ytick.color':MUTED,'axes.edgecolor':'#c8ccc2','axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':PAPER,'axes.facecolor':PAPER,'savefig.facecolor':PAPER})

def axes_style(ax):
 ax.grid(alpha=.3,color='#d4d8ce',zorder=0);ax.set_axisbelow(True);ax.xaxis.set_major_locator(MaxNLocator(5));ax.yaxis.set_major_locator(MaxNLocator(5));ax.tick_params(labelsize=10,length=0,pad=6)

def save(fig,name):
 fig.savefig(OUT/(name+'.png'),dpi=180,bbox_inches=None);plt.close(fig)

def tag(ax,z,i,label,color,offset):
 ax.scatter(*z[i],s=145,facecolors=PAPER,edgecolors=color,linewidths=2,zorder=8)
 ax.annotate(label,z[i],xytext=offset,textcoords='offset points',fontsize=10,fontweight='bold',color=color,ha='left',va='center',bbox=dict(boxstyle='round,pad=.35',fc=PAPER,ec=color,lw=.8),arrowprops=dict(arrowstyle='-',color=color,lw=.8),zorder=9)

# Figure 1: unchanged plotted coordinates, independent density assignments.
fig=plt.figure(figsize=(14,9.2))
fig.text(.055,.95,'Two recurring semantic neighborhoods',fontsize=24,fontweight='bold')
fig.text(.055,.909,'240 Song Ci poems · content-only embeddings · density clustering without poet-style labels',fontsize=12,color=MUTED)
gs=fig.add_gridspec(1,2,left=.065,right=.965,top=.75,bottom=.28,wspace=.16)
legend=[Line2D([0],[0],marker='o',ls='',color=TEAL,label='A  Seasonal scenes & personal longing'),Line2D([0],[0],marker='o',ls='',color=RUST,label='B  History, ambition & reflection'),Line2D([0],[0],marker='o',ls='',color=PURPLE,label='C  Small sorrow pocket (unstable)'),Line2D([0],[0],marker='o',ls='',color=GRAY,label='Unassigned')]
fig.legend(handles=legend,loc='upper left',bbox_to_anchor=(.052,.885),ncol=2,frameon=False,fontsize=10.5,columnspacing=2)
for col,key in enumerate(['tsne','umap']):
 ax=fig.add_subplot(gs[0,col]);z=np.array(coords[key]);lab=labs[key+':m10s5:eom'];axes_style(ax)
 ax.scatter(z[lab<0,0],z[lab<0,1],s=23,c=GRAY,alpha=.65,linewidths=0,zorder=2)
 mapping={0:TEAL,1:RUST} if key=='tsne' else {0:PURPLE,1:TEAL,2:RUST}
 for c,color in mapping.items():ax.scatter(z[lab==c,0],z[lab==c,1],s=30,c=color,alpha=.9,linewidths=0,zorder=3)
 ax.set_xlabel('Layout coordinate 1',fontsize=10);ax.set_ylabel('Layout coordinate 2',fontsize=10)
 ax.set_title('t-SNE' if key=='tsne' else 'UMAP',loc='left',fontweight='bold',fontsize=17,pad=14)
 counts='A 81  ·  B 38  ·  unassigned 121' if key=='tsne' else 'A 98  ·  B 55  ·  C 12  ·  unassigned 75'
 ax.text(0,-.16,counts,transform=ax.transAxes,color=MUTED,fontsize=10.5)
 tag(ax,z,74,'秦观 · 八六子',TEAL,(-50,37) if key=='tsne' else (-125,-35))
 tag(ax,z,231,'吴文英 · 八声甘州',RUST,(25,-34) if key=='tsne' else (-115,40))
 if key=='umap':tag(ax,z,129,'李清照 · 醉花阴',PURPLE,(-115,32))
fig.text(.065,.15,'A  Landscape carries memory and absence',color=TEAL,fontsize=14,fontweight='bold')
fig.text(.065,.106,'秦观《八六子》：夜月一帘幽梦，春风十里柔情。',fontsize=13)
fig.text(.54,.15,'B  Landscape opens onto history and purpose',color=RUST,fontsize=14,fontweight='bold')
fig.text(.54,.106,'吴文英《八声甘州》：名娃金屋，残霸宫城。',fontsize=13)
fig.text(.065,.041,'Clustering: HDBSCAN, minimum cluster size 10, minimum samples 5; seed-42 maps. Gray points are not forced into groups.\nAxes have no fixed literary meaning. Membership agrees for all 97 poems assigned to the two main regions in both maps.',fontsize=9.5,color=MUTED,linespacing=1.6)
save(fig,'01-semantic-neighborhoods')

# Figure 2: more granular candidates, explicitly tentative.
fig=plt.figure(figsize=(14,10))
fig.text(.055,.95,'Five candidate pockets in UMAP',fontsize=23,fontweight='bold')
fig.text(.055,.91,'A finer UMAP subdivision assigns 109 poems; 131 stay unassigned. Smaller boundaries change across projection seeds.',fontsize=11.5,color=MUTED)
ax=fig.add_axes([.065,.20,.49,.64]);z=np.array(coords['umap']);lab=labs['umap:m10s5:leaf'];axes_style(ax)
ax.scatter(z[lab<0,0],z[lab<0,1],c=GRAY,s=25,alpha=.55,linewidths=0)
colors=[PURPLE,'#b29143',RUST,TEAL,'#729a69']
representatives=[129,109,166,101,7]
for c,color in enumerate(colors):
 mask=lab==c;ax.scatter(z[mask,0],z[mask,1],c=color,s=33,alpha=.9,linewidths=0)
 i=representatives[c];ax.scatter(*z[i],s=280,c=PAPER,edgecolors=color,lw=2,zorder=8);ax.text(*z[i],str(c+1),ha='center',va='center',color=color,fontsize=12,fontweight='bold',zorder=9)
ax.set_xlabel('UMAP coordinate 1',fontsize=10);ax.set_ylabel('UMAP coordinate 2',fontsize=10)
notes=[('Private sorrow & solitude','12 poems · 8 by 李清照','梧桐: 3/12 vs 1/228 outside','李清照《醉花阴》'),('Life’s course, purpose & withdrawal','22 poems','何事: 4/22 vs 2/218 outside','叶梦得《水调歌头·秋色渐将晚》'),('Historical & military ambition','13 poems','英雄: 3/13 vs 2/227 outside','张孝祥《水调歌头·和庞佑父》'),('Parting & remembered encounters','44 poems','长亭: 4/44 vs 1/196 outside','周邦彦《兰陵王·柳》'),('Spring longing in intimate settings','18 poems','帘幕: 3/18 vs 5/222 outside','柳永《定风波·自春来惨绿愁红》')]
for c,(title,count,evidence,poem) in enumerate(notes):
 y=.82-c*.137
 fig.text(.60,y,str(c+1),fontsize=14,color=colors[c],fontweight='bold',bbox=dict(boxstyle='circle,pad=.3',facecolor=PAPER,edgecolor=colors[c],lw=1.5))
 fig.text(.635,y,title,fontsize=12.5,fontweight='bold',color=colors[c]);fig.text(.635,y-.027,count,fontsize=11,color=MUTED)
 fig.text(.635,y-.054,evidence,fontsize=11);fig.text(.635,y-.081,poem,fontsize=12)
fig.text(.065,.13,'Treat the 12-poem sorrow island cautiously',fontsize=14,fontweight='bold',color=PURPLE)
fig.text(.065,.112,'It does not remain a separate matched cluster in any of three additional UMAP seed runs.\nIts same-group neighbor rate falls from 33% to 10% when same-author neighbors are excluded.',fontsize=11,color=MUTED,linespacing=1.7,va='top')
fig.text(.065,.055,'Seed 42 · HDBSCAN leaf selection, minimum cluster size 10, minimum samples 5. Counts are poems containing a phrase; “outside” means all other poems.\nTheme names and phrase descriptions were assigned after clustering. Numbered circles identify the representative poems listed at right.',fontsize=9,color=MUTED,linespacing=1.5,va='top')
save(fig,'02-candidate-pockets')

# Figure 3: original-space evidence and literal phrase enrichment.
fig=plt.figure(figsize=(14,9.5))
fig.text(.055,.95,'The broad neighborhoods have support beyond the maps',fontsize=23,fontweight='bold')
fig.text(.055,.909,'Evidence uses original embedding cosine distances; no poet-style labels enter the calculation.',fontsize=12,color=MUTED)
ax=fig.add_axes([.18,.55,.385,.25])
for y,(value,lo,hi,color) in enumerate([(79.18,33.27,49.29,TEAL),(74,22.36,38.91,RUST)]):
 ax.plot([lo,hi],[y,y],color='#bfc4ba',linewidth=13,solid_capstyle='round',zorder=2)
 ax.plot(value,y,'o',color=color,ms=12,zorder=4);ax.text(value+3,y,f'{value:.0f}%',va='center',fontsize=15,color=color,fontweight='bold')
 ax.text((lo+hi)/2,y+.19,f'{lo:.0f}–{hi:.0f}%',ha='center',fontsize=10,color=MUTED)
ax.set_xlim(0,100);ax.set_ylim(1.5,-.65);ax.set_yticks([0,1],['Seasonal / personal','Historical / reflective']);ax.tick_params(axis='y',labelsize=11,length=0)
ax.set_xticks([0,25,50,75,100],['0%','25%','50%','75%','100%']);ax.set_xlabel('Ten nearest neighbors that remain in the same group',fontsize=10);ax.spines[['left','right','top']].set_visible(False);ax.grid(axis='x',color='#d7dbd1',alpha=.5)
fig.text(.07,.837,'Exclude same-author neighbors; keep poem lengths comparable',fontsize=13,fontweight='bold')
fig.text(.105,.485,'Colored dot = observed · gray interval = 95% of 1,000 length-stratified randomizations',fontsize=9.5,color=MUTED)
fig.text(.67,.785,'97 / 97',fontsize=45,fontweight='bold',color=TEAL)
fig.text(.67,.731,'agree across the two maps',fontsize=15,fontweight='bold')
fig.text(.67,.695,'Among poems assigned to a main region\nin both t-SNE and UMAP.\nUnassigned poems are excluded.',fontsize=11.5,color=MUTED,linespacing=1.6,va='top')
fig.text(.07,.405,'The words also differ',fontsize=16,fontweight='bold')
ax=fig.add_axes([.145,.14,.42,.215])
items=[('黄昏',13,98,5,142,TEAL),('长亭',5,98,0,142,TEAL),('离别',5,98,0,142,TEAL),('万里',13,55,6,185,RUST),('江山',6,55,0,185,RUST),('兴亡',4,55,0,185,RUST)]
for y,(word,a,n,b,m,color) in enumerate(items):
 v=100*a/n;w=100*b/m;ax.plot([w,v],[y,y],color='#d1d6cb',lw=3);ax.scatter(w,y,s=40,color='#9ba599',zorder=3);ax.scatter(v,y,s=55,color=color,zorder=4);ax.text(26,y,f'{a}/{n}  vs  {b}/{m}',va='center',fontsize=10,color=color)
ax.set_yticks(range(6),[x[0] for x in items],fontsize=13);ax.set_ylim(5.6,-.6);ax.set_xlim(-1,39);ax.set_xticks([0,10,20],['0%','10%','20%']);ax.spines[['left','top','right']].set_visible(False);ax.tick_params(axis='y',length=0);ax.set_xlabel('Poems containing the phrase',fontsize=10)
fig.text(.67,.337,'Coherent neighborhoods,\nuncertain hard boundaries',fontsize=16,fontweight='bold',linespacing=1.4)
fig.text(.67,.204,'At the tested density settings, HDBSCAN\nfinds no discrete clusters in the original\ncosine space. Projected islands should\nnot be read as a fixed literary taxonomy.',fontsize=11.5,color=MUTED,linespacing=1.6,va='top')
fig.text(.07,.055,'Phrase evidence: seed-42 UMAP main groups, compared with the rest of the corpus. Descriptions are exploratory and post hoc.\nRandomization preserves cluster counts within ten poem-length bands. Original-space density checks used minimum cluster sizes 10/15 and minimum samples 5.',fontsize=9.5,color=MUTED,linespacing=1.5,va='top')
save(fig,'03-original-space-evidence')
print('\n'.join(str(p) for p in OUT.glob('*.png')))

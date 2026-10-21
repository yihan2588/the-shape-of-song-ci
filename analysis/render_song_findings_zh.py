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
plt.rcParams.update({'font.family':['Heiti SC','DejaVu Sans','Arial Unicode MS'],'font.size':12,'text.color':INK,'axes.labelcolor':MUTED,'xtick.color':MUTED,'ytick.color':MUTED,'axes.edgecolor':'#c8ccc2','axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':PAPER,'axes.facecolor':PAPER,'savefig.facecolor':PAPER})

def axes_style(ax):
 ax.grid(alpha=.3,color='#d4d8ce',zorder=0);ax.set_axisbelow(True);ax.xaxis.set_major_locator(MaxNLocator(5));ax.yaxis.set_major_locator(MaxNLocator(5));ax.tick_params(labelsize=10,length=0,pad=6)

def save(fig,name):
 fig.savefig(OUT/(name+'-zh.png'),dpi=180,bbox_inches=None);plt.close(fig)

def tag(ax,z,i,label,color,offset):
 ax.scatter(*z[i],s=145,facecolors=PAPER,edgecolors=color,linewidths=2,zorder=8)
 ax.annotate(label,z[i],xytext=offset,textcoords='offset points',fontsize=10,fontweight='bold',color=color,ha='left',va='center',bbox=dict(boxstyle='round,pad=.35',fc=PAPER,ec=color,lw=.8),arrowprops=dict(arrowstyle='-',color=color,lw=.8),zorder=9)

# Figure 1: unchanged plotted coordinates, independent density assignments.
fig=plt.figure(figsize=(14,9.2))
fig.text(.055,.95,'两种投影中反复出现的语义区域',fontsize=24,fontweight='bold')
fig.text(.055,.909,'240 首宋词 · 仅对正文进行语义嵌入 · 密度聚类不使用词人流派标签',fontsize=12,color=MUTED)
gs=fig.add_gridspec(1,2,left=.065,right=.965,top=.75,bottom=.28,wspace=.16)
legend=[Line2D([0],[0],marker='o',ls='',color=TEAL,label='A  时令景物与离情相思'),Line2D([0],[0],marker='o',ls='',color=RUST,label='B  怀古、抱负与人生感怀'),Line2D([0],[0],marker='o',ls='',color=PURPLE,label='C  愁绪小群（稳定性较弱）'),Line2D([0],[0],marker='o',ls='',color=GRAY,label='未归类')]
fig.legend(handles=legend,loc='upper left',bbox_to_anchor=(.052,.885),ncol=2,frameon=False,fontsize=10.5,columnspacing=2)
for col,key in enumerate(['tsne','umap']):
 ax=fig.add_subplot(gs[0,col]);z=np.array(coords[key]);lab=labs[key+':m10s5:eom'];axes_style(ax)
 ax.scatter(z[lab<0,0],z[lab<0,1],s=23,c=GRAY,alpha=.65,linewidths=0,zorder=2)
 mapping={0:TEAL,1:RUST} if key=='tsne' else {0:PURPLE,1:TEAL,2:RUST}
 for c,color in mapping.items():ax.scatter(z[lab==c,0],z[lab==c,1],s=30,c=color,alpha=.9,linewidths=0,zorder=3)
 ax.set_xlabel('投影坐标 1',fontsize=10);ax.set_ylabel('投影坐标 2',fontsize=10)
 ax.set_title('t-SNE' if key=='tsne' else 'UMAP',loc='left',fontweight='bold',fontsize=17,pad=14)
 counts='A 81 首  ·  B 38 首  ·  未归类 121 首' if key=='tsne' else 'A 98 首  ·  B 55 首  ·  C 12 首  ·  未归类 75 首'
 ax.text(0,-.16,counts,transform=ax.transAxes,color=MUTED,fontsize=10.5)
 tag(ax,z,74,'秦观 · 八六子',TEAL,(-50,37) if key=='tsne' else (-125,-35))
 tag(ax,z,231,'吴文英 · 八声甘州',RUST,(25,-34) if key=='tsne' else (-115,40))
 if key=='umap':tag(ax,z,129,'李清照 · 醉花阴',PURPLE,(-115,32))
fig.text(.065,.15,'A  借景寄托追忆与离情',color=TEAL,fontsize=14,fontweight='bold')
fig.text(.065,.106,'秦观《八六子》：夜月一帘幽梦，春风十里柔情。',fontsize=13)
fig.text(.54,.15,'B  由景生发怀古与抱负',color=RUST,fontsize=14,fontweight='bold')
fig.text(.54,.106,'吴文英《八声甘州》：名娃金屋，残霸宫城。',fontsize=13)
fig.text(.065,.041,'聚类采用 HDBSCAN，最小簇大小 10、最小样本数 5；投影随机种子为 42。灰点保留为未归类。\n坐标轴没有固定的文学含义；在两图中均归入两大区域的 97 首词，其归属完全一致。',fontsize=9.5,color=MUTED,linespacing=1.6)
save(fig,'01-semantic-neighborhoods')

# Figure 2: more granular candidates, explicitly tentative.
fig=plt.figure(figsize=(14,10))
fig.text(.055,.95,'UMAP 中的五个候选主题群',fontsize=23,fontweight='bold')
fig.text(.055,.91,'更细的聚类划分纳入 109 首词，131 首未归类；更换投影随机种子后，小群的边界会变化。',fontsize=11.5,color=MUTED)
ax=fig.add_axes([.065,.20,.49,.64]);z=np.array(coords['umap']);lab=labs['umap:m10s5:leaf'];axes_style(ax)
ax.scatter(z[lab<0,0],z[lab<0,1],c=GRAY,s=25,alpha=.55,linewidths=0)
colors=[PURPLE,'#b29143',RUST,TEAL,'#729a69']
representatives=[129,109,166,101,7]
for c,color in enumerate(colors):
 mask=lab==c;ax.scatter(z[mask,0],z[mask,1],c=color,s=33,alpha=.9,linewidths=0)
 i=representatives[c];ax.scatter(*z[i],s=280,c=PAPER,edgecolors=color,lw=2,zorder=8);ax.text(*z[i],str(c+1),ha='center',va='center',color=color,fontsize=12,fontweight='bold',zorder=9)
ax.set_xlabel('UMAP 坐标 1',fontsize=10);ax.set_ylabel('UMAP 坐标 2',fontsize=10)
notes=[('独处中的愁绪','12 首，其中 8 首为李清照作品','“梧桐”：群内 3/12，群外 1/228','李清照《醉花阴》'),('人生感怀、抱负与归隐','22 首','“何事”：群内 4/22，群外 2/218','叶梦得《水调歌头·秋色渐将晚》'),('怀古与报国壮志','13 首','“英雄”：群内 3/13，群外 2/227','张孝祥《水调歌头·和庞佑父》'),('离别与旧游追忆','44 首','“长亭”：群内 4/44，群外 1/196','周邦彦《兰陵王·柳》'),('闺情春愁','18 首','“帘幕”：群内 3/18，群外 5/222','柳永《定风波·自春来惨绿愁红》')]
for c,(title,count,evidence,poem) in enumerate(notes):
 y=.82-c*.137
 fig.text(.60,y,str(c+1),fontsize=14,color=colors[c],fontweight='bold',bbox=dict(boxstyle='circle,pad=.3',facecolor=PAPER,edgecolor=colors[c],lw=1.5))
 fig.text(.635,y,title,fontsize=12.5,fontweight='bold',color=colors[c]);fig.text(.635,y-.027,count,fontsize=11,color=MUTED)
 fig.text(.635,y-.054,evidence,fontsize=11);fig.text(.635,y-.081,poem,fontsize=12)
fig.text(.065,.13,'这处 12 首词的“愁绪孤岛”，需要谨慎解读',fontsize=14,fontweight='bold',color=PURPLE)
fig.text(.065,.112,'在另外三个随机种子的 UMAP 结果中，它均未保持为可单独匹配的簇。\n排除同一词人的近邻后，同群近邻比例由 33% 降至 10%。',fontsize=11,color=MUTED,linespacing=1.7,va='top')
fig.text(.065,.055,'随机种子 42；HDBSCAN 采用叶簇选择，最小簇大小 10、最小样本数 5。词语计数按包含该词语的作品数统计；“群外”指其余所有作品。\n主题名称和词语描述均为聚类后的解释。图中编号圆圈标出右侧所列的代表作品。',fontsize=9,color=MUTED,linespacing=1.5,va='top')
save(fig,'02-candidate-pockets')

# Figure 3: original-space evidence and literal phrase enrichment.
fig=plt.figure(figsize=(14,9.5))
fig.text(.055,.95,'两大语义区域，也得到原始向量空间的支持',fontsize=23,fontweight='bold')
fig.text(.055,.909,'以原始嵌入向量的余弦距离检验相似性；计算不使用词人流派标签。',fontsize=12,color=MUTED)
ax=fig.add_axes([.18,.55,.385,.25])
for y,(value,lo,hi,color) in enumerate([(79.18,33.27,49.29,TEAL),(74,22.36,38.91,RUST)]):
 ax.plot([lo,hi],[y,y],color='#bfc4ba',linewidth=13,solid_capstyle='round',zorder=2)
 ax.plot(value,y,'o',color=color,ms=12,zorder=4);ax.text(value+3,y,f'{value:.0f}%',va='center',fontsize=15,color=color,fontweight='bold')
 ax.text((lo+hi)/2,y+.19,f'{lo:.0f}–{hi:.0f}%',ha='center',fontsize=10,color=MUTED)
ax.set_xlim(0,100);ax.set_ylim(1.5,-.65);ax.set_yticks([0,1],['时令景物／离情相思','怀古抱负／人生感怀']);ax.tick_params(axis='y',labelsize=11,length=0)
ax.set_xticks([0,25,50,75,100],['0%','25%','50%','75%','100%']);ax.set_xlabel('最近的 10 首作品中，同群作品的比例',fontsize=10);ax.spines[['left','right','top']].set_visible(False);ax.grid(axis='x',color='#d7dbd1',alpha=.5)
fig.text(.07,.837,'排除同一词人的近邻，并按篇幅分层进行随机对照',fontsize=13,fontweight='bold')
fig.text(.105,.485,'彩点：实测值；灰条：按篇幅分层随机置换 1,000 次所得的 95% 区间',fontsize=9.5,color=MUTED)
fig.text(.67,.785,'97 / 97',fontsize=45,fontweight='bold',color=TEAL)
fig.text(.67,.731,'首作品在两图中的归属一致',fontsize=15,fontweight='bold')
fig.text(.67,.695,'仅统计在 t-SNE 与 UMAP 中\n均归入两大区域的作品，\n不含任一图中的未归类作品。',fontsize=11.5,color=MUTED,linespacing=1.6,va='top')
fig.text(.07,.405,'两大区域的用词也有差异',fontsize=16,fontweight='bold')
fig.text(.43,.374,'群内  对比  群外',fontsize=10,color=MUTED)
ax=fig.add_axes([.145,.14,.42,.215])
items=[('黄昏',13,98,5,142,TEAL),('长亭',5,98,0,142,TEAL),('离别',5,98,0,142,TEAL),('万里',13,55,6,185,RUST),('江山',6,55,0,185,RUST),('兴亡',4,55,0,185,RUST)]
for y,(word,a,n,b,m,color) in enumerate(items):
 v=100*a/n;w=100*b/m;ax.plot([w,v],[y,y],color='#d1d6cb',lw=3);ax.scatter(w,y,s=40,color='#9ba599',zorder=3);ax.scatter(v,y,s=55,color=color,zorder=4);ax.text(26,y,f'{a}/{n}  对比  {b}/{m}',va='center',fontsize=10,color=color)
ax.set_yticks(range(6),[x[0] for x in items],fontsize=13);ax.set_ylim(5.6,-.6);ax.set_xlim(-1,39);ax.set_xticks([0,10,20],['0%','10%','20%']);ax.spines[['left','top','right']].set_visible(False);ax.tick_params(axis='y',length=0);ax.set_xlabel('包含该词语的作品比例',fontsize=10)
fig.text(.67,.337,'语义相近的区域确实存在，\n但清晰的簇边界尚不确定',fontsize=16,fontweight='bold',linespacing=1.4)
fig.text(.67,.204,'在已测试的密度参数下，HDBSCAN\n未在原始余弦空间中识别出独立的簇。\n因此，投影中的“孤岛”不宜视为\n固定的文学分类。',fontsize=11.5,color=MUTED,linespacing=1.6,va='top')
fig.text(.07,.055,'词语对比：随机种子 42 的 UMAP 两大群分别与其余作品比较。主题解释属于探索性的事后分析。\n随机置换保持十个篇幅区间内的各群作品数不变。原始空间密度检验使用最小簇大小 10／15、最小样本数 5。',fontsize=9.5,color=MUTED,linespacing=1.5,va='top')
save(fig,'03-original-space-evidence')
print('\n'.join(str(p) for p in OUT.glob('*-zh.png')))

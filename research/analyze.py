from pathlib import Path
import json, csv, collections
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1]
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--base',type=Path,default=ROOT.parent/'professor-code/lecture05_urban_planning_index')
BASE=parser.parse_args().base
SHELTER=ROOT/'research/shelters_original.csv'
# Reproduction: retain original instructor repository sibling and uploaded CSV path above.
s=pd.read_csv(SHELTER,encoding='cp949').fillna('')
def minute(x):
 h,m=map(int,x.split(':'));return h*60+m
DAYS=['월','화','수','목','금','토','일']
def active(row,day,t=840):
 for p in ['기본운영','연장운영','추가운영']:
  if p!='기본운영' and row[p+'_운영여부']!='Y':continue
  ds=row[p+'_요일'].split(','); start=row[p+'_시작시간'];end=row[p+'_종료시간']
  if not start or not end: continue
  a,b=minute(start),minute(end)
  if a==b:continue # ambiguous zero-length / 24h not assumed
  if a<b and day in ds and a<=t<b:return True
  if a>b and ((day in ds and t>=a) or (DAYS[(DAYS.index(day)-1)%7] in ds and t<b)):return True
 return False
s['wed']=s.apply(lambda x:active(x,'수'),axis=1);s['sun']=s.apply(lambda x:active(x,'일'),axis=1)
sg=gpd.GeoDataFrame(s,geometry=gpd.points_from_xy(s['경도'],s['위도']),crs=4326).to_crs(5179)
d=gpd.read_file(BASE/'shp/bnd_dong_seoul.shp').to_crs(5179)
grid=gpd.read_file(BASE/'grid/seoul_100m_grid_2025.geojson').to_crs(5179)
pop=pd.read_csv(BASE/'grid/2024년_인구_다사_100M.csv',encoding='cp949',header=None,names=['year','GRID_CD','stat','pop'])
pop=pop[pop.stat=='to_in_001'][['GRID_CD','pop']]
grid=grid.merge(pop,on='GRID_CD',how='left',validate='one_to_one')
missing=int(grid['pop'].isna().sum())
grid.geometry=grid.geometry.centroid
joined=gpd.sjoin(grid,d[['ADM_CD','ADM_NM','geometry']],how='left',predicate='within')
assert not joined.GRID_CD.duplicated().any()
valid=joined[joined['pop'].notna() & joined.ADM_CD.notna()].copy()
valid['pop']=pd.to_numeric(valid['pop'],errors='raise'); assert (valid['pop']>=0).all()
# Missing population is excluded from both numerator and denominator, not imputed as zero.
xy=np.c_[valid.geometry.x,valid.geometry.y]
for typ in ['all','public']:
 for day in ['wed','sun']:
  z=sg[sg[day] & ((sg['시설구분1']=='공공시설') if typ=='public' else True)]
  dist,_=cKDTree(np.c_[z.geometry.x,z.geometry.y]).query(xy)
  valid[typ+'_'+day]=dist
metrics={}; thresholds=[300,500,800]
for typ in ['all','public']:
 for radius in thresholds:
  k=f'{typ}_{radius}'; metrics[k]={}
  for day in ['wed','sun']:
   valid['covered']=valid['pop']*(valid[typ+'_'+day]<=radius)
   metrics[k][day]=float(valid.covered.sum()/valid['pop'].sum()*100)
rows=[]
for _,r in d.iterrows():
 a=valid[valid.ADM_CD==r.ADM_CD]; total=float(a['pop'].sum());out={'id':r.ADM_CD,'name':r.ADM_NM,'pop':total}
 for typ in ['all','public']:
  for radius in thresholds:
   for day in ['wed','sun']:
    out[f'{typ}_{radius}_{day}']=float(a.loc[a[typ+'_'+day]<=radius,'pop'].sum()/total*100) if total else None
 rows.append(out)
# Static vector map in projected coordinates, geometry simplified for display only.
bounds=d.total_bounds; xmin,ymin,xmax,ymax=bounds
scale=min(920/(xmax-xmin),620/(ymax-ymin))
def ring(coords):
 return 'M'+'L'.join(f'{(x-xmin)*scale+20:.1f},{(ymax-y)*scale+20:.1f}' for x,y in coords)+'Z'
for row,geom in zip(rows,d.geometry.simplify(25,preserve_topology=True)):
 parts=list(geom.geoms) if geom.geom_type=='MultiPolygon' else [geom]
 row['path']=''.join(ring(p.exterior.coords)+''.join(ring(i.coords) for i in p.interiors) for p in parts)
q=sg.to_crs(5179)
shelters=[{'x':round((g.x-xmin)*scale+20,2),'y':round((ymax-g.y)*scale+20,2),'name':r['쉼터명칭'],'type':r['시설구분1'],'wed':bool(r['wed']),'sun':bool(r['sun'])} for (_,r),g in zip(q.iterrows(),q.geometry)]
audit={'facilities':len(s),'wed':int(s.wed.sum()),'sun':int(s.sun.sum()),'public_wed':int(((s['시설구분1']=='공공시설')&s.wed).sum()),'public_sun':int(((s['시설구분1']=='공공시설')&s.sun).sum()),'grids':len(grid),'missing_population_grids':missing,'outside_grids':int(joined.ADM_CD.isna().sum()),'analyzed_grids':len(valid),'population':float(valid['pop'].sum()),'dongs':len(d),'boundary_date':str(d.BASE_DATE.iloc[0]),'ambiguous_equal_time':sum(1 for _,r in s.iterrows() for p in ['기본운영','연장운영','추가운영'] if (p=='기본운영' or r[p+'_운영여부']=='Y') and r[p+'_시작시간'] and r[p+'_시작시간']==r[p+'_종료시간'])}
obj={'rows':rows,'shelters':shelters,'metrics':metrics,'audit':audit,'width':round((xmax-xmin)*scale+40),'height':round((ymax-ymin)*scale+40)}
(ROOT/'data.js').write_text('window.DATA='+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+';',encoding='utf-8')
pd.DataFrame([{k:v for k,v in x.items() if k!='path'} for x in rows]).to_csv(ROOT/'dong_results.csv',index=False,encoding='utf-8-sig')
valid.drop(columns=['geometry','index_right','covered']).to_csv(ROOT/'research/grid_results.csv',index=False,encoding='utf-8-sig')
(ROOT/'research/audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps({'audit':audit,'metrics':metrics},ensure_ascii=False,indent=2))
for row in sorted(rows,key=lambda x:x['all_500_wed']-x['all_500_sun'],reverse=True)[:6]:print(row['id'],row['name'],row['all_500_wed'],row['all_500_sun'])

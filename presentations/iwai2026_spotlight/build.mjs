import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';

const here = path.dirname(fileURLToPath(import.meta.url));
const runtime = '/Users/pat/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const skill = '/Users/pat/.codex/plugins/cache/openai-primary-runtime/presentations/26.1007.11041/skills/presentations';
process.env.RUNTIME_NODE_MODULES = path.join(runtime, 'node/node_modules');
const { Presentation, PresentationFile } = await import(pathToFileURL(
  path.join(runtime, 'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const { finalizePresentation, applyPresentationChartFont } = await import(pathToFileURL(
  path.join(skill, 'container_tools/artifact_tool_utils.mjs')).href);

const version = process.argv[2] || 'v1';
const buildDir = path.join(here, '.build', version);
const finalDir = path.join(here, 'output');
await fs.mkdir(buildDir, { recursive: true });
await fs.mkdir(finalDir, { recursive: true });
const content = JSON.parse(await fs.readFile(path.join(here, 'content.json'), 'utf8'));
const p = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const c = { bg:'#FFFFFF', ink:'#111111', gray:'#575757', pale:'#D4D4D4' };
const font = 'Arial';
p.theme.colorScheme = { name:'Monochrome', themeColors:{accent1:c.ink,accent2:'#777777',accent3:'#BBBBBB',
  accent4:'#444444',accent5:'#999999',accent6:'#DDDDDD',bg1:c.bg,bg2:c.bg,tx1:c.ink,
  tx2:c.gray,dk1:'#000000',dk2:c.ink,lt1:c.bg,lt2:c.pale,hlink:c.ink,folHlink:c.gray} };
function text(s,v,x,y,w,h,size=30,color=c.ink,bold=false,align='left',name='',face=font){
  const t=s.shapes.add({geometry:'textbox',name,position:{left:x,top:y,width:w,height:h},
    fill:'none',line:{fill:'none',width:0}});
  t.text=v; t.text.style={fontSize:size,typeface:face,color,bold,alignment:align,
    verticalAlignment:'top',insets:0,wrap:'square',autoFit:'none'};
  return t;
}
function shape(s,geometry,x,y,w,h,fill=c.ink,stroke='none',width=0){
  return s.shapes.add({geometry,position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width}});
}
function slide(n,kicker,title){
  const s=p.slides.add(); s.background.fill=c.bg;
  text(s,`${String(n).padStart(2,'0')}  /  ${kicker}`,60,30,1120,30,20,c.gray,false,'left','section','Courier New');
  shape(s,'rect',60,74,1160,2);
  if(title) text(s,title,60,104,1160,90,48,c.ink,true,'left','slide-title');
  text(s,'IWAI 2026',60,675,950,24,17,c.gray,false,'left','footer','Courier New');
  text(s,`${n} / 4`,1150,673,70,28,18,c.gray,false,'right','page','Courier New');
  return s;
}
function grid(s,x,y,size,posterior=false){
  const cell=size/4;
  for(let r=0;r<4;r++) for(let col=0;col<4;col++){
    shape(s,'rect',x+col*cell,y+r*cell,cell,cell,c.bg,'#999999',0.8);
    // Dot area is proportional to the analytically computed posterior mass.
    const prob=posterior?(r<2?.1:.025):1/16;
    const d=cell*.4*Math.sqrt(prob*16);
    shape(s,'ellipse',x+(col+.5)*cell-d/2,y+(r+.5)*cell-d/2,d,d);
  }
}
function arrow(s,x,y,w){shape(s,'rightArrow',x,y,w,15);}
function notes(s,i,source){s.speakerNotes.text=`${content.times[i]}\n\n${content.scripts[i]}\n\nSOURCES AND BACKGROUND (not spoken)\n${source}`;}

// 1. The task is a grid with an unknown target, not a navigation problem.
{
 const s=slide(1,'THE SENSING DECISION');
 text(s,'Expected Free Energy\nas Belief-Dependent\nUtility for ρ-POMDPs',60,116,740,226,56,c.ink,true,'left','accepted-title');
 text(s,'Where is the target?\nWhen should we stop looking?',60,376,730,105,36);
 grid(s,880,129,300);
 text(s,'4 × 4 Tileworld',865,454,340,35,27,c.ink,false,'center');
 text(s,'One hidden target.\nAll cells equally likely.',839,502,390,70,25,c.gray,false,'center');
 text(s,'Patrick Cooper and Alvaro Velasquez',60,567,760,44,28);
 text(s,'University of Colorado Boulder',60,614,760,35,23,c.gray);
 notes(s,0,'Accepted paper: paper/paper_iwai2026_abridged.tex, title and Tileworld setup. Current code: rho_aif/environments/tileworld.py. The 4×4 grid is an illustrative uniform belief over one hidden target, not a measured trajectory. There is no agent location, movement, wall or path in this environment. Dot area denotes probability of the target being in that cell.\nOpenReview https://openreview.net/forum?id=jYHOHuD8CO. No generated imagery or external media are used.');
}

// 2. Native grids show the exact Bayesian update for one illustrative signal.
{
 const s=slide(2,'THE ACCEPTED CONTRIBUTION','EFE as belief-dependent utility');
 text(s,'expected reward  +  w × information gain',60,199,1160,66,46,c.ink,true);
 text(s,'Per-step utility in the specified reward-based recursion',60,276,1160,40,26,c.gray);
 grid(s,60,365,180);
 text(s,'Before scanning',50,561,200,36,24,c.gray,false,'center');
 arrow(s,277,444,80);
 text(s,'Noisy scan',254,358,220,40,29);
 text(s,'80% accurate\ncosts 1',260,491,210,74,25,c.gray);
 grid(s,485,365,180,true);
 text(s,'After “top half”',464,561,230,36,24,c.gray,false,'center');
 text(s,'80%',691,389,105,40,29,c.ink,true);
 text(s,'20%',691,480,105,40,29,c.ink,true);
 text(s,'EFE uses w = 1',874,372,340,48,34,c.ink,true);
 text(s,'under the stated\nassumptions',874,429,335,75,26,c.gray);
 text(s,'Illustrative update. Dot area shows cell probability.',60,611,1150,29,21,c.gray);
 notes(s,1,'Accepted paper equivalence proposition; corrected qualifications in paper/full_paper_jair.tex Sections 3.2–3.4. Exact Bayesian beliefs, matched horizon and terminal condition, consistent units, hidden-state-preserving sensing and the same tie rule are required. Both objectives retain future value. Exact reward identification uses log-score preferences with normalizer one, or the proved conditional construction. General empirical rewards use the stated convention; a policy-dependent log normalizer cannot generally be dropped. Canonical w=1 is unit-dependent. The slide-3 empirical convention is one reward unit per bit, whereas exactly nat-canonical weighting is ln(2) in bit units.\nSchematic: TileworldEnv(grid_size=4), uniform prior 1/16, row-high-bit scan action1, signal0. Bayes gives top-eight-cell probabilities .1 each and bottom-eight-cell probabilities .025 each, i.e. half-grid masses .8/.2. The signal is 80% accurate and costs1 reward unit. Dots encode these probabilities by area, not diameter. The lower half remains possible. Independently verified from get_observation_models(), no simulated trajectory.');
}

// 3. Native chart and workbook retain the exact committed scaling values.
{
 const s=slide(3,'THE GRID-WORLD RESULT','More certainty can cost more');
 text(s,'8 × 8 Tileworld. All three planners look ahead two steps.',60,184,1150,43,27,c.gray);
 const keys=['Planning','EFE','Planning+IG'];
 const data=keys.map(k=>content.tileworld[k]);
 const chart=s.charts.add('bar',{
   name:'Tileworld success',position:{left:57,top:253,width:1158,height:354},
   categories:['Reward only (w = 0)\n0 scans\nReward −49.16','EFE (w = 1)\n17.5 scans\nReward −25.86','High weight (w = 100)\n39.5 scans\nReward −30.84'],
   series:[{name:'Success rate',values:data.map(r=>Number(r.success_rate)),fill:c.ink,
     points:[{idx:0,fill:'#AAAAAA'},{idx:1,fill:c.ink},{idx:2,fill:'#AAAAAA'}]}],
   barOptions:{direction:'column',grouping:'clustered',gapWidth:150},hasLegend:false,
   xAxis:{visible:true,textStyle:{fontSize:24,fill:c.ink},line:{fill:c.pale,width:1},majorGridlines:null},
   yAxis:{visible:true,min:0,max:1.2,majorUnit:.5,numberFormatCode:'0%',
     textStyle:{fontSize:22,fill:c.gray},line:{fill:'none',width:0},majorGridlines:{fill:c.pale,width:1,style:'solid'}},
   dataLabels:{showValue:true,showLegendKey:false,showCategoryName:false,showSeriesName:false,
     position:'outEnd',numberFormatCode:'0.0%',textStyle:{fontSize:30,fill:c.ink,bold:true}},
   chartFill:c.bg,chartLine:{fill:'none',width:0},plotAreaFill:c.bg,plotAreaLine:{fill:'none',width:0}
 });
 applyPresentationChartFont(chart,{fontFamily:font});
 text(s,'Success rate',60,234,260,33,23,c.gray);
 text(s,'Means over 5 seeds × 200 episodes. Reward includes scan costs.\nAt this horizon, reward-only planning takes no scans. EFE uses 1 reward unit per bit.',60,620,1140,50,20,c.gray);
 notes(s,2,'Updated values from results/results_tileworld_scaling.csv, grid_size=8, agents Planning/EFE/Planning+IG. All H=2. Five seeds 42,123,456,789,1024 with 200 episodes per seed; row metadata git82ed4eb generated2026-08-20. Values: Planning success.014 (seed SE.0029154759474), scans0, reward−49.16 (seed SE.1749285568454). EFE success.694 (seed SE.010416333328), scans17.496, reward−25.856 (seed SE.677027325889). Planning+IG success.978 (seed SE.005830951895), scans39.52, reward−30.84 (seed SE.386574701707). Native chart values are the unrounded success rates.\nIMPORTANT: w=100 is fixed in this scaling battery, NOT success-tuned. Both other comparisons fix the same model and depth, not compute. No formal significance test is reported for this scaling battery. This is a shallow-horizon illustration, not a claim that arbitrary-depth planning fails or that the benefit increases universally with grid size. At4×4/6×6, the reward-only and EFE rates are close. Reported net reward equals60×success−50−mean_scans and excludes the information bonus. All three reported rewards are negative.');
}

// 4. A schematic mixture diagram is distinct from the measured summary.
{
 const s=slide(4,'SUBSEQUENT WORK','A target for expected sensing usage');
 text(s,'Two policies can bracket the target',60,211,625,43,28);
 // Vertical scale and target line. Geometry is qualitative, without numeric axes.
 shape(s,'rect',108,306,2,244);
 text(s,'Expected usage',60,268,360,35,24,c.gray);
 shape(s,'rect',109,426,523,1,'#777777');
 text(s,'B',64,404,40,48,33,c.ink,true);
 const lo=shape(s,'ellipse',186,492,16,16),hi=shape(s,'ellipse',532,338,16,16);
 s.shapes.connect(lo,hi,{kind:'straight',fromSide:'right',toSide:'left',line:{fill:'#555555',width:2}});
 shape(s,'diamond',347,414,24,24,c.bg,c.ink,2);
 text(s,'Mixture',385,435,180,35,25,c.ink,true);
 text(s,'Lower usage',131,552,220,35,24,c.gray);
 text(s,'Higher usage',456,552,235,35,24,c.gray);
 text(s,'Schematic calibration',120,606,460,30,21,c.gray);
 text(s,'≤ 0.13',760,302,430,97,76,c.ink,true);
 text(s,'observations from target',762,409,450,47,31);
 text(s,'Largest held-out mean error\nacross 12 attainable cases.\nTiger, Diagnosis and Bandit.',762,481,450,112,26,c.gray);
 text(s,'Calibration-derived targets. Per-episode usage can exceed B. Reward need not be optimal.',60,641,1130,27,20,c.gray);
 notes(s,3,'Subsequent research, permitted by the chair according to the presenter. Source: current paper/full_paper_jair.tex, Definition PI-3 and budget-frontier study. The diagram is schematic: two endpoint policies have expected calibration usages on either side of B. A probability mixture can match B in calibration. No numeric curve, simulated trajectory, monotonicity or held-out guarantee is implied.\nresults/results_budget_frontier.csv: twelve attainable policy=mixture rows with held-out usage. Twelve target cases across Tiger/Diagnosis/Bandit correspond to eleven distinct environment-budget pairs because two Tiger requests coincide. Maximum absolute held-out mean usage error=.123, reported≤.13. Three below-range requests fail and are excluded by attainable. Targets came from a predeclared rule on calibration curves, not an operator. The twelve cases do NOT include Tileworld.\nA target on expected usage differs from a per-episode cap and from constrained reward maximization. Public-sensor replay transfer caveat is spoken: later collection batches overspend, as reported in results/results_real_sensor_summary.csv. No deployment claim.');
}

await fs.writeFile(path.join(buildDir,'deck.json'),JSON.stringify(p.toProto(),null,2));
for(let i=0;i<p.slides.items.length;i++){
  const s=p.slides.items[i];
  const png=await p.export({slide:s,format:'png',scale:1.5});
  await fs.writeFile(path.join(buildDir,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
  const layout=await s.export({format:'layout'});
  await fs.writeFile(path.join(buildDir,`slide-${i+1}.layout.json`),await layout.text());
}
const candidatePath=path.join(buildDir,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidatePath);
const finalPath=path.join(finalDir,`iwai2026_spotlight_2026-10-09_${version}.pptx`);
const result=await finalizePresentation({
  workspaceDir:here,candidatePath,finalPath,
  pythonExecutable:path.join(runtime,'python/bin/python3'),
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  explicitTotalSlideCount:4,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[3],
  materializeLiteralChartWorkbooks:true,
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
  fontPolicy:{basis:'design',families:[font,'Courier New']},verifyArtifactToolImport:true,
  receiptPath:path.join(buildDir,'validation.json')
});
// The bundled Artifact Tool PDF exporter cannot resolve its standard-font
// package on this host. Convert the finalized PPTX with bundled LibreOffice.
execFileSync(path.join(runtime,'bin/override/soffice'),
  ['--headless','--convert-to','pdf','--outdir',finalDir,finalPath],{stdio:'inherit'});
console.log(JSON.stringify({finalPath,validation:result},null,2));

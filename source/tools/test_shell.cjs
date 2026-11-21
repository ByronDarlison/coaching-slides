const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

function fixture() {
  const events={}, winEvents={};
  const document={fullscreenElement:null,querySelectorAll:()=>[],querySelector:()=>null,addEventListener:(name,fn,options)=>{events[name]={fn,options};}};
  const opened=[];
  const window={innerWidth:390,innerHeight:844,matchMedia:()=>({matches:true}),open:(url)=>opened.push(url),addEventListener:(name,fn)=>{winEvents[name]=fn;}};
  const context={document,window,Element:class {},requestAnimationFrame:fn=>fn(),history:{replaceState(){}},IntersectionObserver:class{observe(){}},globalThis:{}};
  vm.createContext(context);
  const code=fs.readFileSync(path.join(__dirname,'../shared/deck/shell.js'),'utf8').replace('new SlidePresentation();','globalThis.Controller = SlidePresentation;');
  vm.runInContext(code,context);
  const controller=Object.create(context.globalThis.Controller.prototype);
  return {controller,document,window,events,winEvents,opened};
}

test('mobile vertical swipes scroll while horizontal swipes navigate',()=>{
  const {controller,events}=fixture();let moves=[];
  controller.next=()=>moves.push('next');controller.previous=()=>moves.push('previous');controller.setupTouchNavigation();
  const target={closest:()=>null};
  events.touchstart.fn({changedTouches:[{clientX:200,clientY:500}]});
  events.touchend.fn({target,changedTouches:[{clientX:190,clientY:200}]});
  assert.deepEqual(moves,[]);
  events.touchstart.fn({changedTouches:[{clientX:300,clientY:500}]});
  events.touchend.fn({target,changedTouches:[{clientX:100,clientY:490}]});
  assert.deepEqual(moves,['next']);
});

test('height-only mobile viewport changes preserve reading position',()=>{
  const {controller,window,winEvents}=fixture();let calls=0;
  controller.updateFullscreenControl=()=>{};controller.alignAfterResize=()=>calls++;controller.setupFullscreen();
  window.innerHeight=780;winEvents.resize();assert.equal(calls,0);
  window.innerWidth=844;winEvents.resize();assert.equal(calls,1);
});

test('body scrolling updates the active slide using a capture listener',()=>{
  const {controller,events}=fixture();let updates=0;
  controller.currentSlide=0;controller.viewportSettling=false;
  controller.slides=[{getBoundingClientRect:()=>({top:-900})},{getBoundingClientRect:()=>({top:100})}];
  controller.updateInterface=()=>updates++;controller.setupIntersectionObserver();
  assert.equal(events.scroll.options.capture,true);
  events.scroll.fn({target:{}});
  assert.equal(controller.currentSlide,1);assert.equal(updates,1);
});

test('on a small screen, tapping a drawing opens the in-page zoom view and never leaves the deck',()=>{
  const {events,opened,document}=fixture();
  const made=[];
  const el=(tag)=>{const node={tag,children:[],attrs:{},style:{},dataset:{},listeners:{},classList:{add(){},remove(){}},
    setAttribute(k,v){this.attrs[k]=v;},removeAttribute(k){delete this.attrs[k];},addEventListener(n,fn){this.listeners[n]=fn;},
    append(...kids){this.children.push(...kids);},appendChild(kid){this.children.push(kid);},querySelectorAll:()=>[],
    contains(){return false;},focus(){},remove(){this.removed=true;}};made.push(node);return node;};
  document.createElement=el;document.body=el('body');document.activeElement=null;
  const panel=(src,{fit=false,qr=false}={})=>{
    const img={naturalWidth:1800,getAttribute:(k)=>k==='src'?src:null,cloneNode:()=>el('img'),
      closest:(sel)=>sel==='.story-frame--fit'?(fit?{}:null):sel==='[data-deck-qr]'?(qr?{}:null):sel==='.slide'?{dataset:{title:'Your 3HAG on one page.'}}:null};
    return {closest:(sel)=>sel==='.story-panel--art'?{querySelector:()=>img}:null};
  };
  const views=()=>made.filter((node)=>node.className==='art-zoom'&&!node.removed).length;
  events.click.fn({target:panel('./assets/photo.jpg')});
  events.click.fn({target:panel('./assets/deck-qr.svg',{qr:true})});
  events.click.fn({target:panel('./assets/path.svg',{fit:true})});
  events.click.fn({target:{closest:()=>null}});
  assert.equal(views(),0);
  events.click.fn({target:panel('./assets/map.svg')});
  assert.equal(views(),1);
  const view=made.find((node)=>node.className==='art-zoom');
  assert.equal(view.attrs.role,'dialog');
  const close=made.find((node)=>node.className==='art-zoom-button'&&node.textContent==='Close');
  const canvas=made.find((node)=>node.className==='art-zoom-canvas');
  assert.equal(canvas.style.width,'1170px');
  close.listeners.click();
  assert.equal(views(),0);
  assert.deepEqual(opened,[]);
});

test('links open a slide by name, and the old numeric links still work',()=>{
  const {controller}=fixture();
  controller.slides=[{dataset:{name:'opening-welcome'}},{dataset:{name:'bhag-path-bhag'}},{dataset:{}}];
  assert.equal(controller.hashIndex('#bhag-path-bhag'),1);
  assert.equal(controller.hashIndex('#slide-3'),2);
  assert.equal(controller.hashIndex('#slide-99'),2);
  assert.equal(controller.hashIndex('#no-such-slide'),0);
  assert.equal(controller.hashIndex(''),0);
  assert.equal(controller.slideHash(1),'#bhag-path-bhag');
  assert.equal(controller.slideHash(2),'#slide-3');
});

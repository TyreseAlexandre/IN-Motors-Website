const WA='258867596098';
const menuButton=document.querySelector('.menu-btn');
if(menuButton){
  menuButton.addEventListener('click',()=>{const open=document.body.classList.toggle('menu-open');menuButton.setAttribute('aria-expanded',open)});
  document.querySelectorAll('.nav-links a').forEach(a=>a.addEventListener('click',()=>{document.body.classList.remove('menu-open');menuButton.setAttribute('aria-expanded','false')}));
}

document.querySelectorAll('.faq-q').forEach(button=>button.addEventListener('click',()=>{const item=button.parentElement;document.querySelectorAll('.faq-item').forEach(other=>{if(other!==item){other.classList.remove('open');other.querySelector('.faq-q').setAttribute('aria-expanded','false')}});const open=item.classList.toggle('open');button.setAttribute('aria-expanded',open)}));

const form=document.getElementById('quoteForm');
const formOk=document.getElementById('formOk');
if(form){
  form.addEventListener('submit',event=>{
    event.preventDefault();
    if(!form.checkValidity()){form.reportValidity();return;}
    const v=id=>document.getElementById(id).value.trim();
    const message=`Olá, IN Motors. Gostaria de solicitar uma cotação personalizada.\n\nNome: ${v('name')}\nTelefone: ${v('phone')}\nMarca: ${v('make')}\nModelo: ${v('model')||'Sem preferência'}\nAno pretendido: ${v('year')||'Sem preferência'}\nOrçamento máximo: ${v('budget')}\nOrigem: ${v('origin')}\nTransmissão: ${v('transmission')}\nOutros detalhes: ${v('notes')||'Nenhum'}\n\nAguardo o vosso contacto. Obrigado.`;
    const url=`https://wa.me/${WA}?text=${encodeURIComponent(message)}`;
    form.classList.add('sending');
    const win=window.open(url,'_blank','noopener');
    if(!win){location.href=url;}
    form.classList.remove('sending');
    if(formOk){formOk.classList.add('show');setTimeout(()=>formOk.classList.remove('show'),6000);}
    form.reset();
  });
}

const bar=document.getElementById('scrollbar');
const nav=document.querySelector('.nav');
const onScroll=()=>{
  const max=document.documentElement.scrollHeight-window.innerHeight;
  if(bar)bar.style.width=(max>0?window.scrollY/max*100:0)+'%';
  if(nav)nav.classList.toggle('scrolled',window.scrollY>10);
};
onScroll();
addEventListener('scroll',onScroll,{passive:true});

const navMap=new Map();
document.querySelectorAll('.nav-links a[href*="#"]').forEach(a=>{const id=a.getAttribute('href').split('#')[1];if(id)navMap.set(id,a)});
const spy=new IntersectionObserver(entries=>{entries.forEach(e=>{if(e.isIntersecting){navMap.forEach(a=>a.classList.remove('active'));const a=navMap.get(e.target.id);if(a)a.classList.add('active');}});},{rootMargin:'-45% 0px -50% 0px'});
document.querySelectorAll('main section[id]').forEach(s=>spy.observe(s));

const revealEls=document.querySelectorAll('.reveal');
if('IntersectionObserver' in window){
  const io=new IntersectionObserver((entries,obs)=>{entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');obs.unobserve(e.target);}});},{rootMargin:'0px 0px -10% 0px'});
  revealEls.forEach(el=>io.observe(el));
}else{
  revealEls.forEach(el=>el.classList.add('in'));
}

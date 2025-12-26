// 간단한 네비게이션 토글 및 모달 제어
document.addEventListener('DOMContentLoaded', function(){
  const navToggle = document.getElementById('navToggle');
  const nav = document.getElementById('nav');
  navToggle && navToggle.addEventListener('click', ()=>{
    if(nav.style.display === 'flex') nav.style.display = '';
    else nav.style.display = 'flex';
  });

  // 부드러운 스크롤
  document.querySelectorAll('a[href^="#"]').forEach(a=>{
    a.addEventListener('click', function(e){
      const target = document.querySelector(this.getAttribute('href'));
      if(target){ e.preventDefault(); target.scrollIntoView({behavior:'smooth', block:'start'});
        if(window.innerWidth <= 800 && nav) nav.style.display = '';
      }
    })
  });

  // modal
  const modal = document.getElementById('modal');
  const openBtn = document.getElementById('openDetails');
  const closeBtn = document.getElementById('modalClose');
  openBtn && openBtn.addEventListener('click', ()=>{ modal.setAttribute('aria-hidden','false'); });
  closeBtn && closeBtn.addEventListener('click', ()=>{ modal.setAttribute('aria-hidden','true'); });
  modal && modal.addEventListener('click', (e)=>{ if(e.target === modal) modal.setAttribute('aria-hidden','true'); });
});

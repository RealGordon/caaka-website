function loginsuccess(r){
    hidePreloader();  
    if (r.status !== "success") {loginerror();return;}
    menu=document.getElementById('caakamenu');
    var p,data;
    data={h:['/static/admin.html','/logout'],
    t:['Admin','Logout']};
    els=[];
    els[0]=menu.lastElementChild;
    els[1]=$(els[0]).clone()[0];
    console.log(els[1].toString());
    for (var i=0;i<2;++i){
      p=els[i]
      a=p.children[0];
      a.href=data.h[i];
    a.innerText=data.t[i]+ ( i==1 ? "("+r.name+")" : "");
    }
    menu.appendChild(els[1]);
     } 
function loginerror(){
        hidePreloader();
        }

     $(document).ready(function() {
        //Preloader
        
        
        (function(){
        var spinner=$('#internalspinner')[0];
        var parent=spinner.parentElement;
        spinner.style.display="block";
        spinner.className="caakaspinner1";
        parent.style.display="block";
        parent.className="spinner-wrapper";
        })();
		var x=new XMLHttpRequest();
		x.open('GET','/home/get/poster');
		x.responseType="json";
		x.onreadystatechange=function(){
			if (x.readyState==4 && x.status==200){
				displayposter(x.response);
			}
		}
		x.send();
        //$.get({
        //url:'/home/get/poster',
        //dataType:'application/json',
        //success:displayposter
        //});
        function displayposter(r){
        var pdata='',idata='',pi,ii;
        for (var i=0;i<r.position.length || i<r.info.length ; ++i){
         pi=r.position[i],ii=r.info[i];
        if (pi) {
        pdata= pdata+'<li>'+pi+'</li>'}
        if (ii){
        idata= idata+'<li>'+ii+'</li>'}};
        var p=document.createElement('p');p.innerText='Date published: '+r.date;
        $('#joblist').html(pdata)[0].parentElement.appendChild(p);
        $('#infolist').html(idata);
        if (r.blob_name) $('#imageposter')[0].src= r.blob_name;
        if (r.advertpostid) advertpostid=r.advertpostid;
        }
        
        
        var args1=window.location.href.split('?');
        if (args1.length !== 2) {hidePreloader(); return;}
        if (args1[1].split('=').length !== 2) {hidePreloader(); return;}
        
        var x=new XMLHttpRequest();
        x.open('GET','/login/user?session=true');
        x.setRequestHeader('Content-Type','application/x-www-form-urlencoded')
        x.responseType="json";
        x.onreadystatechange=function(){
            if (x.readyState==4 && x.status==200){
                loginsuccess(x.response);
            }
        }
        x.onerror=function(){loginerror()};
        x.send();


        });
        

var menu,els;
function placeposter(url){
document.getElementById('poster').style="background-image:url("+url+")";}
var data={},conformspinner;
function whenready(){
document.forms.contactform.onsubmit=function(){
var inputs=$("form input");
conformspinner=new cSpinner('conformspinner');
conformspinner.action();

inputs.each(function(i,el){
 data[el.name]=el.value;
 });
data[this.message.name]=this.message.value;
$.post({url:'/submit/contactform',
data:data,
success:afterSubmit,
error:afterSubmit,
});
return false;
}}
$(whenready);
function afterSubmit(data,formstatus){
//success- data,status, xhr/jxhr
//error - xhr/jxhr,status
conformspinner.action();
var formdisplay=true;
if (formstatus!=="success") formdisplay=false; 
var message = formdisplay ? "Your Message has been sent!"  : "Sorry Error occurred, try again";
var form=document.forms.contactform;
//form.previousElementSibling.textContent=message;
$("form[name='contactform'] input").attr('disabled',false).text('');
form.getElementsByTagName('textarea')[0].value="";
form.getElementsByTagName('textarea')[0].disabled=false;
alert(message);
}
 var textposter,cvarea;
function uploadCV(){
//places the form into the page
cvarea=document.getElementById('cvarea');
var joblist=document.getElementById('joblist').getElementsByTagName('li');
textposter=document.getElementById('textposter');
var jlistdom="<ul><b>Select Position</b>";
if (joblist.length > 0) { 
var p;
for (p in joblist) { 
if (!(joblist.hasOwnProperty(p))) {continue;}
mytext=joblist[p].innerText;
jlistdom= jlistdom +
'<li><input class="w3-margin" type="checkbox" name="industries" value='+
'"'+mytext+'"'+'><label>'+mytext+'</label></li>';
}
jlistdom=jlistdom+'</ul>';}
cvarea.removeChild(textposter);
var cvform=$('<div class="section-content" >'+
'<div style="display: none"; class="caakaspinner-wrapper" id="cvformwrapper">'+
'<div class="caakaloader" id="cvformspinner" style="display: none"></div></div>'+
'<p></p>'+  
'<form id="cvform" onsubmit="cvformSubmit(this);return false;" name="formCV" action="/submit/CV" method="POST" '+
' enctype="multipart/form-data">'+'<div class="w3-container">'+
 jlistdom + '</div>'+"<input type='hidden' name='advertpostid'"+
"value="+'"'+advertpostid+'"'+">"+
'<div class="w3-container">'+
 ' <label for="myfile">Select your CV File:</label>'+
  '<input type="file" id="myfile" name="CV" class="w3-input" required><br><br>'+
  '</div><input type="submit" class="w3-button w3-blue" value="Submit">'+
 ' <button onclick="cancelCV(this)" class="w3-button w3-red"> Cancel</button>'+
 '</form></div>')[0];
 cvarea.appendChild(cvform);
}
function cancelCV(el,status){
	if (el) {
cvarea.removeChild(cvarea.lastElementChild);
cvarea.appendChild(textposter);
return false;
}
var p=document.getElementById('cvform').previousElementSibling;
var message;
if (!status) {
//close spinner and provide error message
message="Error uploading CV, try again";}
else {message="CV uploading success"; }
//uploding cv success 
p.innerText=message;
return false;
}
var cvformspinner;
function cvformSubmit(formel){
	var cvdata=new FormData(formel);
	var x=new XMLHttpRequest;
    x.open('POST','/submit/CV');
    //x.timeout=10000;
    if (!cvformspinner) cvformspinner=new cSpinner('cvformspinner',x);
	cvformspinner.action();
    x.onreadystatechange=function(){
    	if (x.readyState==4 && x.status==200){
    		cvformspinner.action();
			alert("document(s) upload success");
			cancelCV(formel);
   	}
   }
    x.send(cvdata);
   cvformspinner.spinnerChecker(15000);
}
function spinnerAction() {
//show or hide spinner
var loader=document.getElementById(this.spinner_id),change;
if (loader.style.display==="none") {change="block"; this.status=true;}
else {change="none"; this.status=false;}
document.getElementById(loader.parentNode.id).style.display = change;
 loader.style.display = change;
}
function cSpinner(spinner_id,x) {
    if (x) this.x=x;
    this.attempt=0;
this.spinner_id=spinner_id;
this.status=true; this.id=Date.now();
}
function spinnerChecker(time){
var s=this;
function wrapper() {if (s.status) {
    if (s.x) {
       if (s.attempt<1) {
           s.attempt++
           ;return s.spinnerChecker(15000);
       } else if (s.attempt<=2 && s.x.readyState!=4) {
           s.attempt++;
        return s.spinnerChecker(10000);
       };

    }
s.action(); var message;
if (s.x) s.x.abort();
if (s.spinner_id=="cvformspinnner") message="Error uploading CV, try again";
else message="error occurred please try again";
alert(message)}
}
setTimeout(wrapper,time);
}
cSpinner.prototype.action=spinnerAction;
cSpinner.prototype.spinnerChecker=spinnerChecker;
var advertpostid="n/a";
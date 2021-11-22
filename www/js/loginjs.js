window.onload=function(){
document.forms.LogIn.onsubmit=function(e){
    var msg=$('#message1');
    var req=new XMLHttpRequest;req.open('POST','/login/user');
    req.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
    req.timeout=12000;
    if (!loginformspinner) loginformspinner=new cSpinner('formspinner'); 
    loginformspinner.action();
    req.onreadystatechange=function(e){
    if (req.readyState===4 && req.status==200) { 
    if (req.responseText==="success") {
    loginformspinner.spinnerChecker(0);
    window.location="/?status=admin";}
    else {msg=msg.text("Error: Failed to Login, "+req.responseText)[0];
    msg.className="w3-text-red";
    loginformspinner.action();}
    }}
    loginformspinner.spinnerChecker(15000);
    req.onerror =function() {loginformspinner.spinnerChecker(0);
    msg.text('Error coccured try again')};
    req.send($( this ).serialize());return false;
    }
}
var loginformspinner;
function spinnerAction() {
    //show or hide spinner
    var loader=document.getElementById(this.spinner_id),change;
    if (loader.style.display==="none") {change="block"; this.status=true;}
    else {change="none"; this.status=false;}
    document.getElementById(loader.parentNode.id).style.display = change;
     loader.style.display = change;
    }
function cSpinner(spinner_id) {
    this.spinner_id=spinner_id;
    this.status=true; this.id=Date.now();
    }
function spinnerChecker(time){
    var spinner=this;
    function wrapper() {if (spinner.status) {spinner.action();
    if (spinner.spinner_id=="cvformspinnner") message="Error uploading CV, try again";
    else message="error occurred please try again";
    alert(message)}
    }
    setTimeout(wrapper,time);
    }
cSpinner.prototype.action=spinnerAction;
cSpinner.prototype.spinnerChecker=spinnerChecker;


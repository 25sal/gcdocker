// File app.js
var strophe = require("node-strophe").Strophe;
var Strophe = strophe.Strophe;
var Papa = require("papaparse");
global.XMLHttpRequest = require('xhr2');
var request = require('request');
const Blob = require("cross-blob");
// Global patch (to support external modules like is-blob).
global.Blob = Blob;
var FormData = require('form-data');

var server = "greencharge.simulator";
var BOSH_SERVICE = 'http://greencharge.local:5280/http-bind';
var http_post_port=10021;
var jid="demo@greencharge.local/actormanager";
var passwd = "demo";


var connection = null;
var messages = [];
var auto = 1;
var post_url="http://"+server+":"+http_post_port+"/postanswer";
var devices ={};


  var fs = require("fs");
  var logstream = fs.createWriteStream('/home/scheduler/debug.log', { 
        flags: "a", encoding: "utf8", mode: 0644 
    });
  
  function mylog(msg)
  {
	  logstream.write(msg+'\n');
	  }
  
  connection = new Strophe.Connection(BOSH_SERVICE);
  connection.rawInput = connection.rawOutput = mylog;
  connection.connect(jid, passwd, onConnect);
  






function log(msg, msgid) 
{
	var respond='';
	

	if(msgid!=null)
	{
	 var elems = messages[msgid].getElementsByTagName('body');
	 var body = Strophe.getText(elems[0]);
	 body = body.replace(/\s+/g, ' ');
	if(body.startsWith("LOAD")){
	   if(auto==0)
	 	{   respond = "AST.html"
			$('#log').append('<td><div class="col-md-6"> <button onclick="loadview('+msgid+')" class="btn btn-primary" type="button" id="loadview"  data-toggle="modal" data-target="#modalResponse">RESPONSE</button></div>');    
	    	$('#log').append('</td></tr></table></div>');
		}
		else
		{
			
			var msg  = messages[msgid];
			var tokens = body.split(' ');
			var from = msg.getAttribute('from');
			var to = msg.getAttribute('to');
			var response = "";
			var ast =parseInt(tokens[6]) + 600;
			response = "ASSIGNED_START_TIME " + tokens[1] + " " + tokens[2] + " " + tokens[3]  ;
			//REPLACE TOKENS[3] WITH AST
			
			var reply = new Strophe.Builder("message",{to: from, from: to, type: 'chat'}).c("body").t(response);
			connection.send(reply.tree());
			console.log("SENT response:" + response);
			response = "SCHEDULED";
                        var reply = new Strophe.Builder("message",{to: from, from: to, type: 'chat'}).c("body").t(response);
	                connection.send(reply.tree());	
               }

		 }
          else if (body.startsWith("HC")){

                if(auto!=0)
			{
	
				var tokens = body.split(' ');
				var csvresponse="";
				jsonResponse = {}
          			jsonResponse["subject"]= "HC_PROFILE";

          			//jsonResponse["sim_id"]=jsonRequest.sim_id;
          			jsonResponse["time"]=tokens[4];
          			jsonResponse["id"]=tokens[1];
					Papa.parse(tokens[3], {
                                           download:true,
					   delimiter: ' ',
					   step: function (result, parsers) {
						if(result.data.length==3)
						csvresponse+=result.data[0]+ " " + result.data[1] + "\n";
                        //console.log("Row data:"+ result.data);
						//console.log("Error:"+ result.error);
						
						},
                                           complete: function(result,file){
							console.log("complete");
							
							var b =new Blob([csvresponse]);
							var fd = new FormData();

							const fileBuffer = Buffer.from(csvresponse, 'utf-8');
							fd.append('csvfile',fileBuffer ,'test.csv');
							
							fd.append('response', JSON.stringify(jsonResponse));
							
							fd.submit({
								host: server,
								port: http_post_port,
								path: '/postanswer',
								method: 'POST'
							  }, function(err, res) {
								console.log(res.statusCode);
							  });
							

							}
					});
			
				}
		}
        else if(body.startsWith("CREATE_EV "))
	{
	   var tokens = body.split(' ');
	   var ev_id = tokens[1];
	   var capacity = parseInt(tokens[2]);
	   var max_ch_pow_ac = parseFloat(tokens[3]);
	   devices[ev_id] = {"capacity": capacity, "max_ch_pow_ac": max_ch_pow_ac};
	} 
	else if(body.startsWith("EV "))
	  if(auto!=0)
		{
		var tokens = body.split(' ');
                
		var ev_id = tokens[1];
		var capacity = devices[ev_id]["capacity"];
		var max_ch_pow_ac = devices[ev_id]["max_ch_pow_ac"];
		var dep_time = parseInt(tokens[3]);
		var arr_time = parseInt(tokens[4]);
		var target_soc = parseInt(tokens[7]);
		var arriv_soc = parseInt(tokens[2]);
		var sim_time = parseInt(tokens[8]);
               if(sim_time==dep_time){

		var booked_charge = capacity*(target_soc-arriv_soc)/100;
          var available_energy= max_ch_pow_ac*(dep_time-arr_time)/3600;
          var charged_energy= available_energy;
          var charged_0 =capacity*arriv_soc/100;
          if(available_energy>=booked_charge)
             charged_energy = booked_charge;
          var charging_time = 3600*charged_energy/max_ch_pow_ac;
          var csvstr = arr_time+" "+ charged_0+"\n";
          csvstr += (charging_time+arr_time)+" "+(charged_energy+charged_0);
          console.log(csvstr);
	  var form = new FormData();
          var b =new Blob([csvstr]);
	  jsonResponse = {}
	  jsonResponse["subject"]= "EV_PROFILE";

    	  //jsonResponse["sim_id"]=jsonRequest.sim_id;
          jsonResponse["time"]=tokens[27];
          jsonResponse["id"]=tokens[2];
	  form.append("response", JSON.stringify(jsonResponse));
	  const fileBuffer = Buffer.from(csvstr, 'utf-8');
	  form.append('csvfile',fileBuffer ,'test.csv');
           console.log("ciao");
          console.log(JSON.stringify(form));
	  form.submit({
		host: server,
		port: http_post_port,
		path: '/postanswer',
		method: 'POST'//,
		//headers: {'x-test-header': 'test-header-value'}
	  }, function(err, res) {
            console.log("AAAAAAAAAAAAAAAAAAAAAAAA");
	    console.log(err);
            //$.notify("EV Profile Uploaded");
	    console.log("AAAAAAAAAAAAAAAAAAAAAAAAAAA");
	    console.log("EV_PROFILE sent");
	 	 });
              
                        


    		  }

		}//msg!=null	
		}
		 return true;
	}

function onConnect(status)
{
    if (status == Strophe.Status.CONNECTING) {
	console.log('Strophe is connecting.');
    } else if (status == Strophe.Status.CONNFAIL) {
		console.log('Strophe failed to connect.');
   } else if (status == Strophe.Status.DISCONNECTING) {
	console.log('Strophe is disconnecting.');
    } else if (status == Strophe.Status.DISCONNECTED) {
		console.log('Strophe is disconnected.');
   } else if (status == Strophe.Status.CONNECTED) {
	console.log('Strophe is connected.');
	//console.log('ECHOBOT: Send a message to ' + connection.jid +  to talk to me.');

	connection.addHandler(onMessage, null, 'message', null, null,  null); 
	var temp =new Strophe.Builder("presence", null);
	connection.send(temp.tree());
    }
}

function onMessage(msg) {
    var to = msg.getAttribute('to');
    var from = msg.getAttribute('from');
    var type = msg.getAttribute('type');
    var elems = msg.getElementsByTagName('body');

    if (type == "chat" && elems.length > 0) {
	var body = elems[0];

	var messagebody =  Strophe.getText(body);

	messages.push(msg);
	console.log('Message from ' + from + ': ' + Strophe.getText(body));
	log('Message from ' + from + ': ' + Strophe.getText(body),messages.length-1);
    



    }

    // we must return true to keep the handler alive.  
    // returning false would remove it after it finishes.
    return true;
}





  

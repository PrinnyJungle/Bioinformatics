function clearField(a){document.getElementById(a).value=""}function jumpLink(a){window.location.hash=a}(function(){function a(g,e,f){if(g){$("#"+g).removeClass(e);$("#"+g).addClass(f)}}function d(e){a(e,"XDinactive","XDactive")}function c(e){a(e,"XDactive","XDinactive")}function b(){$('a[rel="tooltip"]').each(function(){var e=this.id=="linkInstalledDetails"?"auto":250;var f=$("#"+$(this).attr("href")).html();$(this).qtip({style:{name:"cream",width:e,border:{width:-5,radius:5,color:"#fff1a8"},background:"#fff1a8",color:"#000"},position:{adjust:{screen:true}},content:f,show:"mouseover",hide:{when:"mouseout",effect:"fade"}}).click(function(){return false})})}$(DocumentHelper.getDocument()).ready(function(){$("#runReportTbh_vinId").select();$(".XDinactive").mouseover(function(){d(this.id)});$(".XDinactive").mouseout(function(){c(this.id)});b()})})();
$(document).ready(function(){
	//render markdown
	$("*.comment-content").each(function(i,sel){
		$(sel).html(markdown.toHTML($(sel).text()));
	});
	
	// set label color
	$('.label').each(function(){
		if( $(this).data("color") )
		{
			$(this).data('textcolor', getContrastYIQ($(this).data("color")));
		}
	});

	//show all open issues
	activateStateButton("filter_state_open");

	//show first issue
	$('*.issue-item').removeClass('active');
	$('*.issue-item').first().addClass('active');
	reloadContent();
});

function reloadContent(){
	var state;
	if ($("#filter_state_open").hasClass("active")){
		state = "open";
	} else {
		state = "closed";
	}

	var milestones = [];
	$('.milestone.active').each(function(i,sel){
		milestones[i] = $(sel).data('milestone');
	});

	var labels = [];
	$('.label.active').each(function(i,sel){
		labels[i] = $(sel).data('label');
	});

	//filter items
	var items = $('.issue-item');
	items.removeClass('visible');

	//filter for state
	items = $(items).filter('[data-state='+state+ ']')
	

	//filter for milestones
	if(milestones.length == 0){
		// no milestone filter selected
	} else if(milestones[0] == "None"){
		//not in any milestone filter selected
		items = $(items).filter("[data-milestone='']")
	} else {
		//milestone filter selected
		items = $(items).filter("[data-milestone='" + milestones[0] + "']")
	}

	//filter for labels
	if(labels.length == 0){
		// no label filter selected
	} else if(milestones == ["None"]){
		//no label filter selected
		items = $(items).filter("[data-label='']")
	} else {
		//milestone filter selected
		for(var l=0; l < labels.length; l++){
			items = $(items).filter("[data-labels*='" + labels[l] + "']")
		}
	}

	items.addClass('visible')


	if(!$(".issue-item.active").hasClass('visible')){
		//show first issue
		$('*.issue-item.active').removeClass('active');
		$('*.issue-item.visible').first().addClass('active');
	}
	$(".issue ").removeClass('visible');
	$(".issue[data-issue=" + $('.issue-item.active').data('issue') + "]").addClass('visible');
	
	$(".commentCount").each(function(){
		$(this).text(commentCount($(this).data('count')));
	});
}

function activateStateButton(id){
	if(id == "filter_state_open"){
		opp_id = "filter_state_closed";
	} else {
		opp_id = "filter_state_open";
	}
	if(!$("#" + id).hasClass("active")){
		$("#" + id).addClass("active");
		$("#" + opp_id).removeClass("active");
	} else {
		$("#" + opp_id).removeClass("active");
	}
	reloadContent();
}

function activateIssue(id){
	$('.issue-item').removeClass('active');
	$('.issue-item[data-issue=' + id +']').addClass('active');
	reloadContent()
}

function selectMilestone(id){
	if($('.milestone.active').data('milestone') == id){
		$('.milestone').removeClass('active');
	} else {
		$('.milestone').removeClass('active');
		$('.milestone[data-milestone=' + id + "]").addClass('active');
	}
	reloadContent()
}

function toggleLabel(id){
	l = $('.label[data-label=' + id + "]");
	if(id == 'None'){
		$('.label').removeClass('active')
		l.addClass('active')
	} else {
		if(l.hasClass('active')){
			l.removeClass('active');
			l.find('a').css('color','');
		} else {
			l.addClass('active');
			l.find('a').css('color',l.data('textcolor'));
		}
	}
	reloadContent()
}

function parseTime(time){
	return new Date((time || "").replace(/-/g,"/").replace(/[TZ]/g," "));
}

function timeAgo(date) {

    var seconds = Math.floor((new Date() - date) / 1000);

    var interval = Math.floor(seconds / 31536000);

    if (interval > 1) {
        return interval + " years";
    }
    interval = Math.floor(seconds / 2592000);
    if (interval > 1) {
        return interval + " months";
    }
    interval = Math.floor(seconds / 86400);
    if (interval > 1) {
        return interval + " days";
    }
    interval = Math.floor(seconds / 3600);
    if (interval > 1) {
        return interval + " hours";
    }
    interval = Math.floor(seconds / 60);
    if (interval > 1) {
        return interval + " minutes";
    }
    return Math.floor(seconds) + " seconds";
}

function commentCount(comments){
	if(comments === 1)
	{
		return "1 comment";
	}
	return comments+" comments";
}

function getContrastYIQ(hexcolor){
	var r = parseInt(hexcolor.substr(0,2),16);
	var g = parseInt(hexcolor.substr(2,2),16);
	var b = parseInt(hexcolor.substr(4,2),16);
	var yiq = ((r*299)+(g*587)+(b*114))/1000;
	return (yiq >= 128) ? 'black' : 'white';
}
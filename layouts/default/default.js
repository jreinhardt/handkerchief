$(document).ready(function(){
	//render markdown
	$("*.comment-content").each(function(i,sel){
		$(sel).html(markdown.toHTML($(sel).text()));
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
		} else {
			l.addClass('active');
		}
	}
	reloadContent()
}


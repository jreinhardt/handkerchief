issue_data = $issue_data;
comment_data = $comment_data;
function reload_content(id){
	var comment_node = document.getElementById("comments");
	while (comment_node.hasChildNodes()) {
		comment_node.removeChild(comment_node.lastChild);
	}
	for(var i = 0; i < issue_data.length; i++){
		if(issue_data[i]["number"] == id){
			document.getElementById("title").firstChild.nodeValue = issue_data[i]["title"];

			var comment = document.createElement("div");
			comment.setAttribute("class","comment");
			comment.innerHTML = markdown.toHTML(issue_data[i]["body"]);
			comment_node.appendChild(comment);
			for(var j = 0; j < comment_data.length; j++){
				if(comment_data[j]["issue_url"] == issue_data[i]["url"]){
					var comment = document.createElement("div");
					comment.setAttribute("class","comment");
					comment.innerHTML = markdown.toHTML(comment_data[j]["body"]);
					comment_node.appendChild(comment);
				}
			}
			break;
		}
	}
}
function clear_issues(){
	//clear menu
	filtered_items = document.getElementById("filtered");
	while (filtered_items.hasChildNodes()) {
		filtered_items.removeChild(filtered_items.lastChild);
	}
	//clear active class
	document.getElementById("filter_state_open").setAttribute("class","")
	document.getElementById("filter_state_closed").setAttribute("class","")
	document.getElementById("filter_no_milestone").setAttribute("class","")
	for(var i = 0; i < issue_data.length; i++){
		document.getElementById("filter_state_" + issue_data[i]['state']).setAttribute("class","")
		if(issue_data[i]['milestone'] != null){
			document.getElementById("filter_milestone_" + issue_data[i]['milestone']['title']).setAttribute("class","")
		}
	}
}
function add_issue(issue){
	filtered_items = document.getElementById("filtered");
	var issue_title = document.createTextNode(issue["title"])
	var issue_link = document.createElement("a");
	issue_link.setAttribute("href",'javascript:reload_content(' + issue["number"].toString() + ')')
	issue_link.appendChild(issue_title);

	var issue_item = document.createElement("li")
	issue_item.appendChild(issue_link)

	filtered_items.appendChild(issue_item);
}
function filter_state(state){
	clear_issues();
	document.getElementById("filter_state_" + state).setAttribute("class","active")
	for(var i = 0; i < issue_data.length; i++){
		if(issue_data[i]['state'] != state){
			add_issue(issue_data[i]);
		}
	}
}
function filter_label(label){
	clear_issues();
	document.getElementById("filter_label_" + label).setAttribute("class","active")
	for(var i = 0; i < issue_data.length; i++){
		for(var j = 0; j < issue_data[i]['labels'].length; j++){
			if(issue_data[i]['labels'][j]['name'] == label){
				add_issue(issue_data[i]);
			}
		}
	}
}
function filter_milestone(title){
	clear_issues();
	document.getElementById("filter_milestone_" + title).setAttribute("class","active")
	for(var i = 0; i < issue_data.length; i++){
		if(issue_data[i]['milestone'] != null){
			if(issue_data[i]['milestone']['title'] == title){
				add_issue(issue_data[i]);
			}
		}
	}
}
function filter_not_in_milestone(){
	clear_issues();
	document.getElementById("filter_no_milestone").setAttribute("class","active")
	for(var i = 0; i < issue_data.length; i++){
		if(issue_data[i]['milestone'] == null){
			add_issue(issue_data[i]);
		}
	}
}
function filter_all(){
	clear_issues();
	for(var i = 0; i < issue_data.length; i++){
		add_issue(issue_data[i]);
	}
}


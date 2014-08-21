try{FOIMachine = FOIMachine;}catch(err){FOIMachine = {};}
FOIMachine.events = FOIMachine.events !== undefined ? FOIMachine.events : _.extend({}, Backbone.Events);
FOIMachine.templates = FOIMachine.templates !== undefined ? FOIMachine.templates : {};
FOIMachine.templates.agencySummaryTemplate = '\
  <% if (!hidden || can_edit) { %> \
      <div class="item agency <% if(!can_edit){ %> noedit <% } %> <% if(contact_counts < 1 && !justCreated) { %> hidden <% } %>" id="<%= id %>" >\
        <% if (hidden) { %>\
            <span class="deleted-msg">Agency deleted, edit to unhide </span><br/>\
        <% } %>\
        <div class="agency-container  <% if (hidden) { %>deleted<% } %> <% if (can_edit) { %>editspace<% } %>" id="<%= id %>">\
            <span id="<%= id %>" class="request-text"><%= name %></span> <i class="fa fa-caret-square-o-down toggle"></i>\
            <div class="agency-government-name" id="<%= id %>"> <%= government_name %>, <span class="contact-cnt"><%= contact_counts %></span> contact<% if(contact_counts != 1) { %>s<% } %></div>\
            <% if (can_edit) { %> \
                <a href="#" class="edit-agency-btn" data-agencyid="<%= id %>">Edit Agency</a>\
            <% } %>\
        </div>\
        <span class="hide-these-contacts">Loading contacts...</span>\
        <div class="contacts">\
            Loading contacts...\
        </div>\
      </div>\
  <% } %>\
';
FOIMachine.templates.editAgencyTemplate = '' +
    '<div id="editAgencyDrawer">' +
        '<div class="error" id="editAgencyError"><div>' +
        '<div class="formRow"><label>Name:</label> <input id="input_edit_agency_name" value="<%- name %>" /></div>' +
        '<div class="formRow"><label>Government:</label>' +
            '<select id="select_edit_agency_government"></select>' +
        '</div>' +
        '<div class="formRow"><label class="delete-obj">Delete Agency:</label> <input type="checkbox" id="input_edit_agency_hidden" <% if (hidden) { %> checked <% } %> /></div>' +
        '<button id="saveExistingAgency" class="btn">Save</button>' + 
        '<button id="cancelExistingAgency" class="btn">Cancel</button>' + 
    '</div>';
FOIMachine.templates.selectedAgencyTemplate = '\
  <div class="recipient">\
    <span class="name" id="selected-agency-id-<%= id %>"><%= name %></span>\
    <a href="#" class="remove-agency-button" id="<%= id %>"><i class="remove-icon fa fa-times-circle"></i></a>\
  </div>\
';
var Agency = Backbone.Model.extend({
    initialize: function(attributes){
        if(attributes !== null){
            this.attributes = attributes;
            this.set("can_edit", FOIMachine.userData.isEditor || this.get("created_by") === FOIMachine.userData.username)
            this.set("contact_counts", this.get("can_edit") ? this.get("editor_contact_cnt") : this.get("pub_contact_cnt"));
        }
    },
    url: function(){
        if(this.attributes.id !== undefined)
            return '/api/v1/agency/' + this.attributes.id + '/';
        return '/api/v1/agency/';
    }
});
var AgencyCollection = Backbone.Collection.extend({
    model: Agency,
    initialize: function(models, options){
    },
    url: function(){
        return '/api/v1/agency/';
    }
});
var SelectedAgencyView = Backbone.View.extend({
    initialize: function(options){
        this.template = _.template(FOIMachine.templates.selectedAgencyTemplate);
        this.el = $(options.el);
        this.el.empty();
        this.agency = options.agency !== undefined ? options.agency : undefined;
    },
    render: function(){
        if(this.agency === undefined)
            return false;
        this.el.empty();
        var me = this;

        var data = {
            'id': this.agency.get('id'),
            'name': this.agency.get('name')
        }
        me.el.append(me.template(data));
        $("a.remove-agency-button").on("click", function(e){
            var target = e.srcElement || e.target;
            target = $(target);
            var thisId = target.attr('id');
            //me.el.empty();
            FOIMachine.events.trigger('agencyDeSelected', {});
            return false;
        });
    },
    selectAgency: function(agency, render){
        this.agency = agency;
        if(render === undefined || render !== undefined && render === true)
            this.render();
    },
    clearSelection: function(){
        this.el.empty();
    }
});
var AgencySummaryView = Backbone.View.extend({
    className: 'item-container',
    model: Agency,
    initialize: function(options){
        this.parent = options.parent;
        this.template = _.template(FOIMachine.templates.agencySummaryTemplate);
        this.editAgencyTemplate = _.template(FOIMachine.templates.editAgencyTemplate);
        this.contactsView = new ContactSelectionView({el: this.el, parent: this});
        this.model = options.model;
        this.contactCnt = this.model.get("can_edit") ? this.model.get("editor_contact_cnt") : this.model.get("pub_contact_cnt");
    },
    events: {
        "click .agency-container": "clickAgency",
        "click #cancelExistingAgency": "cancelEditAgency",
        "click #saveExistingAgency": "saveExistingAgency",
        "click a.edit-agency-btn": "editAgency",
        "click .hide-these-contacts": "hideContacts",
    },
    getTemplateData: function(){
        data = {
            'name': this.model.get("name"),
            'government_name' : this.model.get("government_name"),
            'contact_counts': (this.model.get("can_edit") ? this.model.get("editor_contact_cnt") : this.model.get("pub_contact_cnt")),
            'id': this.model.get("id"),
            'hidden' : this.model.get("hidden"),
            'can_edit' : (FOIMachine.userData.isEditor || this.model.get("created_by") === FOIMachine.userData.username),
            'justCreated': this.model.get("justCreated") === undefined ? false : this.model.get("justCreated")
        };
        return data;
    },
    userCanEditContactInMe: function(){
        this.$(".item.agency").removeClass("noedit");
        this.model.set("contact_counts", ++this.contactCnt);
        this.$(".contact-cnt").html(this.model.get("contact_counts"));
        this.model.set("can_edit", true);
    },
    render: function(){
        this.parent.$(".agencies").append(this.el);
        this.$el.append(this.template(this.getTemplateData()));
    },
    renderNew: function(){
        this.parent.$(".agencies").prepend(this.el);
        this.$el.append(this.template(this.getTemplateData()));
    },
    hideContacts: function(){
        this.$(".hide-these-contacts").toggle();
        this.$(".contacts").toggle("slide", {"direction": "up"});
    },
    clickAgency: function(){
        this.$(".hide-these-contacts").toggle();
        if(this.$(".contacts").css("display") !== "none"){
            this.$(".contacts").toggle("slide", {"direction": "up"});
            this.$(".toggle").removeClass("fa-caret-square-o-up");
            this.$(".toggle").addClass("fa-caret-square-o-down");
        }else{
            FOIMachine.events.trigger('agencySelected', {agency: this.model});
            this.contactsView.getContactsForAgency(this.model.get("id"));
            this.$(".toggle").removeClass("fa-caret-square-o-down");
            this.$(".toggle").addClass("fa-caret-square-o-up");
        }
        //this.parent.hideMe();
        this.clicked = true;
        return false;
    },
    editAgency: function(e){
        var me = this;
        e.preventDefault();
        var target = e.srcElement || e.target;
        target = $(target);
        this.$('#editAgencyDrawer').remove();
        this.$el.prepend(me.editAgencyTemplate(me.model.attributes));
        this.$(".agency-container").hide();
        this.$(".edit-agency-btn").hide();

        govs =  _.sortBy(me.parent.govcoll.models, function(gov){return gov.get("name")})
        govs.forEach(function(gov){
            $('#select_edit_agency_government').append('<option value=' + gov.get("id") + " " + (gov.get("id") == me.model.attributes.government ? "selected" : "") + ">" + gov.get("name") + "</option>");
        });
        return false;
    },
    saveExistingAgency: function(ee){
        var me = this;
        ee.preventDefault();
        me.model.set({
            name: me.$('#input_edit_agency_name').val(),
            government: me.$('#select_edit_agency_government').val(),
            hidden: me.$('#input_edit_agency_hidden').prop('checked')
        });
        me.model.save({},
        {
            success: function(theAgency, response, options){
                me.$('#editAgencyDrawer').remove();
                me.$el.html(me.template(me.getTemplateData()));
                FOIMachine.utils.showUserMsg("Agency saved!");
            },
            error: function(one, two, three){
                //message = this.xhr.responseText;
                if(this.xhr === undefined){
                    message = three.xhr.responseText;
                }else {
                    message = this.xhr.responseText;
                }
                FOIMachine.events.trigger('agencyCreationError', {message: message});
                FOIMachine.utils.showUserMsg(message);
            }
        });
        return false; 
    },
    cancelEditAgency: function(){
        this.$(".agency-container").show();
        this.$(".edit-agency-btn").show();
        this.$('#editAgencyDrawer').remove();
        return false;
    },
});
var AgencySelectionView = Backbone.View.extend({
    initialize: function(options){
        this.template = _.template(FOIMachine.templates.agencySummaryTemplate);
        this.el = options.el;
        this.agencies = new AgencyCollection();
        this.offset = 0;
        this.limit = 25;
        this.refetch();
        this.getGovs();
        this._agencies = [];
        this.showOnlyWithContacts = false;
        this.nfetches = 0;
        this.mostRecentReply = 0;
        this.total = -1;
        this.showOnlyWhatICanedit = false;
    },
    refetch: function(){
        var renderme = _.bind(this.render, this);
        var thisfetch = this.nfetches;
        var that = this;
        var callback = function(e){
            // Drop out-of-order replies
            that.total = e.meta.total_count;
            if (thisfetch < that.mostRecentReply) {
                return;
            }
            that.mostRecentReply = thisfetch;
            renderme();
        }
        var sortByAgency = $('#sortByAgency').hasClass('selected');
        var data = [
            {name: 'limit', value: this.limit},
            {name: 'order_by', value: sortByAgency ? 'name' : 'government__name'},
            {name: 'order_by', value: sortByAgency ? 'government__name' : 'name'},
            {name: 'offset', value: this.offset}
        ];
        if (this.query) {
            data.push({name: 'query', value: this.query});
        }
        if (this.showOnlyWithContacts) {
            data.push({name: 'has_contacts', value: 1 });
        }
        if (this.showOnlyWhatICanedit) {
            data.push({name: "show_can_edit", value: 1})
        }
        this.agencies.fetch({success: callback, data: data});
        this.nfetches++;
    },
    events: {
        "keyup #agency-search-box": "search",
        "click #showHideByContacts[type='checkbox']": "showHideAgenciesWithContacts",
        "click #showHideByEdits[type='checkbox']": "showHideByEdits",
        "click a.add-agency-btn, #cancelNewAgency": "cancelAddAgency",
        "click #saveNewAgency": "saveNewAgency",
        "click #nextPage" : "nextPage",
        "click #prevPage" : "prevPage"
    },
    setCurrentPageCount: function(){
        this.$(".count .current").html((this.offset/this.limit)+1);
    },
    nextPage: function() {
        this.offset += this.limit;
        this.disableControls();
        this.setCurrentPageCount();
        this.refetch();
    },
    prevPage: function(){
        this.offset -= this.limit;
        this.disableControls();
        this.setCurrentPageCount();
        this.refetch();
    },
    cancelAddAgency: function(e){
        e.preventDefault();
        $('.addAgency').toggle();
        return false;
    },
    showHideAgenciesWithContacts: function(e){
        this.$("#agency-search-box").val('');
        this.disableControls();
        if(this.$("#showHideByContacts").is(':checked')){
            this.$(".item.hidden").show();
            this.showOnlyWithContacts = false;
        }else{
            this.$(".item.hidden").hide();
            this.showOnlyWithContacts = true;
        }
        this.offset = 0;
        this.refetch();
    },
    showHideByEdits: function(e){
        this.disableControls();
        this.$("#agency-search-box").val('');
        if(this.$("#showHideByEdits").is(':checked')){
            this.$(".item.noedit").hide();
            this.showOnlyWhatICanedit = true;
        }else{
            this.$(".item.noedit").show();
            this.showOnlyWhatICanedit = false;
        }
        this.offset = 0;
        this.refetch();
    },
    search: _.throttle(function(e){
        var origTarget = e.srcElement || e.target;
        var letters = $(origTarget).val();
        if (letters) {
            this.query = letters;
        }
        else {
            this.query = null;
        }
        this.$("#showHideByContacts").prop('checked', true);
        this.showOnlyWithContacts = false;
        this.$(".item.hidden").show();
        this.offset = 0;
        this.refetch();
    }, 500, {leading: false}),
    back: function(){
        this.render(this._agencies)
    },
    sortByState: function(model){
        // Sort by state name (e.g. Maine, Oregon)
        // Then by agency name (e.g. State Police, City of Portland)
        // So City of Portland (Maine) < State Police (Maine) < City of Portland (Oregon) < State Police (Oregon)
        return model.attributes.government_name + model.attributes.name;

    },
    sortByAgencyName: function(model){
        // Sort by agency name (e.g. State Police, City of Portland)
        // Then by state name (e.g. Maine, Oregon)
        // So City of Portland (Maine) < City of Portland (Oregon) < State Police (Maine) < State Police (Oregon)
        return model.attributes.name + model.attributes.government_name;
    },
    getSort: function(){
        var sortFunction  = this.sortByState;
        if ($('#sortByAgency').hasClass('selected'))
        {
            sortFunction = this.sortByAgencyName;
        }
        return sortFunction;
    },
    clickAgency: function(e){
        e.preventDefault();
        var target = e.srcElement || e.target;
        target = $(target);
        if(target.hasClass("edit-agency"))
            return;
        //var thisId = target.parent().attr("id")
        var thisId = target.attr("id");
        var model = _.find(models, function(model){
            return model.attributes.id === thisId;
        });
        FOIMachine.events.trigger('agencySelected', {agency: model, el: this.el});
        return false;
    },
    saveNewAgency: function(e){
        e.preventDefault();
        var me = this;
        var newAgency = new Agency({
            name : me.$('#input_name').val(),
            government: me.$('#select_government').val()
        });
        newAgency.save({},{
            success: function(theAgency, response, options){
                this.$('div.addAgency').toggle();
                me.agencies.unshift(newAgency);
                newAgency.set("justCreated", true);
                var asv = new AgencySummaryView({model: newAgency, parent: me});
                asv.renderNew();
                FOIMachine.events.trigger('agencyCreated', {agency: newAgency});
                FOIMachine.utils.showUserMsg("Agency succesfully created!");
            },
            error: function(){
                data = {message: 'Error. Does that agency already exist?'};
                FOIMachine.utils.showUserMsg(data.message);
                FOIMachine.events.trigger('agencyCreationError', data); 
            }
    
        });
        return false;
    },
    getGovs: function(){
        var me = this;
        if(this.govcoll !== undefined)
            return this.govcoll;
        this.govcoll = new GovernmentCollection();
        this.govcoll.fetch({data:{limit: 10000}, success: function(){
            govs = _.sortBy(me.govcoll.models, function(gov){return gov.get("name")})
            govs.forEach(function(gov){
                me.$('#select_government').append('<option value=' + gov.get("id") + ">" + gov.get("name") + "</option>");
            });
         }
        });
        return this.govcoll;
    },
    disableControls: function(){
        this.$("a.add-agency-btn").css('opacity', '.2');
        this.$("a.add-agency-btn").css('pointer-events', 'none');
        this.$("#agency-search-box").css('opacity', '.2');
        this.$("#agency-search-box").css('pointer-events', 'none');
        this.$('#nextPage').addClass('disabled');
        this.$('#prevPage').addClass('disabled');
        this.$("#showHideByContacts").css("opacity", ".2")
        this.$("#showHideByContacts").css("pointer-events", "none");
        this.$("#showHideByEdits").css("opacity", ".2")
        this.$("#showHideByEdits").css("pointer-events", "none");
    },
    enableControls: function(){
        this.$("a.add-agency-btn").css('opacity', '1');
        this.$("a.add-agency-btn").css('pointer-events', 'all');
        this.$("#agency-search-box").css('opacity', '1');
        this.$("#agency-search-box").css('pointer-events', 'all');
        this.$('#nextPage').removeClass('disabled');
        this.$('#prevPage').removeClass('disabled');
        this.$("#showHideByContacts").css("opacity", "1")
        this.$("#showHideByContacts").css("pointer-events", "all");
        this.$("#showHideByEdits").css("opacity", "1")
        this.$("#showHideByEdits").css("pointer-events", "all");
    },
    render: function(collection){
        this.enableControls();
        this.$("a.add-agency-btn").css('opacity', '1');
        this.$("a.add-agency-btn").css('pointer-events', 'all');
        this.$("#agency-search-box").css('opacity', '1');
        this.$("#agency-search-box").css('pointer-events', 'all');
        this.$(".loading-note").remove();
        this._agencies = collection;
        $("#agency-search-box").attr('contenteditable','true');
        this.$(".item-container").remove();
        var models = (_.isUndefined(collection) || collection.models.length <= 0) ? this.agencies.models : collection.models;
        this.setCurrentPageCount();
        this.$(".count .total").html(Math.round((this.total/this.limit) + 1));
        if (this.offset == 0) {
            this.$('#prevPage').addClass('disabled');
        }
        else {
            this.$('#prevPage').removeClass('disabled');
        }
        if (models.length == this.limit) {
            // This won't work 100% of the time but will work fairly well
            // and will eliminate the need to run a SQL count
            this.$('#nextPage').removeClass('disabled');

        }
        else {
            this.$('#nextPage').addClass('disabled');

        }
        var sortFunction  = this.sortByState;
        if ($('#sortByAgency').hasClass('selected'))
        {
            sortFunction = this.sortByAgencyName;
        }
            
        models = _.sortBy(models, sortFunction);
        var me = this;
        _.each(models, function(obj){
            var asv = new AgencySummaryView({
                model: obj,
                parent: me 
            });
            asv.render();
        });
        me.$('.agencies').scrollTop(0);
        $('.sortToggle').click(function(){
            var $this = $(this);
            if ($this.hasClass('selected'))
            {
                return;
            }
            $('.sortToggle').removeClass('selected');
            $this.addClass('selected');
            me.offset = 0;
            me.refetch();
        });
        if(this.$("#showHideByContacts").is(':checked')) {
            this.$(".item.hidden").show();
        }
        else {
            this.$(".item.hidden").hide();
        }
    },
    toggle: function(){
        if(this.$el.css('display') !== 'none'){
            this.$el.hide();
            FOIMachine.events.trigger("agencySelectionClosed", {});
            return "Choose an agency";
        }
        this.$el.show();
        return "Close agencies";
    },
    hideMe: function(){
        //this.$el.hide();
        $(".agency-wrapper").hide();
        return "Choose agencies";
    },
    showMe: function(){
        $(".agency-wrapper").show();
    }
});

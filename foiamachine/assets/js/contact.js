try{FOIMachine = FOIMachine;}catch(err){FOIMachine = {};}
FOIMachine.events = FOIMachine.events !== undefined ? FOIMachine.events : _.extend({}, Backbone.Events);
FOIMachine.templates = FOIMachine.templates !== undefined ? FOIMachine.templates : {};
FOIMachine.templates.selectedContactTemplate = '\
  <div class="recipient">\
    <a href="#" class="remove-contact-btn" id="<%= id %>"><i class="remove-icon fa fa-times-circle"></i></a>\
    <span class="contact" id="selected-contact-id-<%= id %>"> <%= contactInfo %> </span>\
    <span class="agency"><%= agency_names %></span>\
    <span class="name"> <%= name %> </span>\
    <span class="name"> <%= phone %> </span>\
    <span class="name"> <%= address %> </span>\
  </div>\
';
FOIMachine.templates.selectContactTemplate = '\
  <% if (!hidden || can_edit) { %> \
      <div class="item contact" data-contactid="<%= id %>" >\
        \
        <% if (hidden) { %>\
            <span class="deleted-msg">Contact deleted, edit to unhide </span><br/>\
        <% } %>\
        <div class="contact-container <% if (can_edit) { %> editspace <% } %>" id="<%= id %>">\
            <span class="select-this-contact">Select this contact</span>\
            <span id="<%= id %>"><%= name %></span>\
            <span id="<%= id %>" class="note"><%= email %></span>\
            <span id="<%= id %>" class="note"><%= address %></span>\
            <span id="<%= id %>" class="note"><%= phone %></span>\
            <% if(notes.trim() !== ""){ %><span id="<%= id %>" class="note">User notes: <%= notes %></span> <% }else{ %><span class="note" id="<%= id %>">No user notes</span> <% } %> \
            <% if (can_edit) { %> \
                <a href="#" class="edit-contact-btn" id="<%= id %>" data-contactid="<%= id %>">Edit Contact</a>\
            <% } %> \
            <div class="warning">\
                <span class="message">It appears you have already selected one or more contacts from another agency. You can only send a request to one agency. Are you sure you want to select this contact? Doing so will clear your current selection.</span>\
                <span class="yes">Use this contact</span>\
            </div>\
        </div>\
      </div>\
  <% } %>\
';
FOIMachine.templates.addContactTemplate = '\
  <div class="addContact">\
    <div id="addContactDrawer">\
        <div class="error" id="addContactError"></div>\
        <div class="formRow"><label>First Name</label> <input id="input_first_name" placeholder="optional" /></div>\
        <div class="formRow"><label>Last Name</label> <input id="input_last_name" placeholder="optional"/></div>\
        <div class="formRow"><label>Notes</label> <input id="input_notes" placeholder="optional"/></div>\
        <div class="formRow"><label>Title</label> <input id="input_title" placeholder="optional"/></div>\
        <div class="formRow"><label>Email</label> <input id="input_email" placeholder="unique, preferred"/></div>\
        <div class="formRow"><label>Phone</label> <input id="input_phone" placeholder="optional"/></div>\
        <div class="formRow"><label>Address</label> <input id="input_address" placeholder="optional" /></div>\
        <button id="saveNewContact" class="btn">Save</button>\
        <button id="cancelNewContact" class="btn">Cancel</button>\
    </div>\
  </div>\
  <div id="editContactDrawer" style="display:none"></div>\
';
FOIMachine.templates.editContactTemplate = '' +
'<div id="editContactDrawer">' +
    '<div class="editContact">' +
        '<div class="error" id="addContactError"></div>' +
        '<div class="formRow"><label>First Name:</label> <input id="edit_input_first_name" placeholder="optional" value = "<%- first_name %>" /></div>' +
        '<div class="formRow"><label>Last Name:</label> <input id="edit_input_last_name" placeholder="optional" value="<%- last_name %>" /></div>' +
        '<div class="formRow"><label>Notes:</label><input id="edit_input_notes" placeholder="optional" value ="<% print(_.escape("" || typeof notes != \"undefined\" && notes || "")) %>" /></div>' +
        '<div class="formRow"><label>Contact Title:</label> <input id="edit_input_title" placeholder="optional" value = "<% print(_.escape("" || typeof titles != \"undefined\" && titles[0] || "")) %>" /></div>' +
        '<div class="formRow"><label>Email:</label><input id="edit_input_email" placeholder="unique, required" value = "<% print(_.escape("" || typeof emails != \"undefined\" && emails[0] || "")) %>" /></div>' +
        '<div class="formRow"><label>Phone:</label><input id="edit_input_phone" placeholder="optional" value ="<% print(_.escape(typeof phone!= \"undefined\" && phone[0] || "")) %>"  /></div>' +
        '<div class="formRow"><label>Address:</label> <input id="edit_input_address" placeholder="optional" value = "<% print(_.escape(typeof addresses != \"undefined\" && addresses[0] || "")) %>" /></div>' +
        '<div class="formRow"><label class="delete-obj">Delete Contact:</label> <input type="checkbox" id="edit_input_hidden" <% if (hidden) { %> checked <% } %> /></div>' +
        '<button id="saveExistingContact" class="btn">Save</button>' +
        '<button id="cancelExistingContact" class="btn">Cancel</button>' +
    '</div>' +
'</div>';
  

var Contact = Backbone.Model.extend({
    initialize: function(attributes){
        this.attributes = attributes;
        if(FOIMachine.utils.onloadSelectedContacts !== undefined && FOIMachine.utils.onloadSelectedContacts[this.get("id")] !== undefined)
            this.attributes.selected = true;
    },
    url: function(){
        if(this.attributes.id !== undefined)
            return '/api/v1/contact/' + this.attributes.id + '/';
        return '/api/v1/contact/';
    },
    getAgencyId: function(){
        var arr = this.get("agencies")[0].split("/")
        return arr[arr.length - 2];
    }
});
var ContactCollection = Backbone.Collection.extend({
    model: Contact,
    initialize: function(models, options){
    },
    url: function(){
        return '/api/v1/contact/';
    }
});
var SelectedContactView = Backbone.View.extend({
    className: "selected-contact-container",
    model: Contact,
    initialize: function(options){
        this.model = options.contact;
        this.parent = options.parent;
        this.template = _.template(FOIMachine.templates.selectedContactTemplate);
        this.contact = options.contact !== undefined ? options.contact : undefined;
        this.model.on("change", function(){
            if(this.model.get("selected") !== undefined && this.model.get("selected")){
                this.render();
            }else if(!this.model.get("selected")){
                this.removeContact()
            }
        }, this);
    },
    events: {
        "click a.remove-contact-btn": "removeContactBtn"
    },
    removeContactBtn: function(e){
        this.removeContact();
        FOIMachine.events.trigger('contactDeSelected', {contactId: this.contact.get('id')});
        return false;
    },
    removeContact: function(){
        this.$el.empty();
        this.model.set("selected", false);
        this.model.off( null, null, this );
        return false;
    },
    render: function(){
        this.parent.append(this.el);
        if(this.contact === undefined)
            return false;
        var me = this;
        var name = this.model.get("first_name") !== undefined ? this.model.get('first_name') : "";
        name += this.model.get("last_name") !== undefined ? " " + this.model.get("last_name") : "";
        var data = {
            'id': this.model.get('id'),
            'contactInfo': this.model.get("emails")[0] === undefined ? this.model.get("addresses")[0] : this.model.get("emails")[0],
            'agency_names': this.model.get("agency_names"),
            'name': name,
            'address': this.model.get("addresses")[0],
            'phone': this.model.get("phone")[0]
        };
        //this.model.set("selected", true);
        me.$el.html(me.template(data));
    },
    selectContact: function(contact, render){
        this.model = contact;
        this.model.on("change", this.render, this);
        if(render === undefined || render !== undefined && render === true)
            this.render();
    },
    clearSelection: function(){
        //this.model.set("selected", false);
        this.$el.empty();
    }
});
var ContactSummaryView = Backbone.View.extend({
    className: 'item-container',
    model: Contact,
    initialize: function(options){
        this.parent = options.parent;
        this.template = _.template(FOIMachine.templates.selectContactTemplate);
        this.editContactTemplate = _.template(FOIMachine.templates.editContactTemplate);
        this.model = options.model;
        this.model.on("change", function(){
            this.setSelectedUnselected();
            this.showWarning();
        }, this);
    },
    events: {
        "click .select-this-contact": "clickContact",
        "click #cancelExistingContact": "cancelEditContact",
        "click #saveExistingContact": "saveExistingContact",
        "click a.edit-contact-btn": "editContact",
        "click .warning": "acceptWarning"
    },
    showWarning: function(){
        if(this.model.get("contested") !== undefined && this.model.get("contested"))
            this.$(".warning").toggle("slide", {"direction": "up"});
    },
    acceptWarning: function(){
        if(this.model.get("contested") !== undefined && this.model.get("contested")){
            FOIMachine.events.trigger('contactWarningAccepted', {contact: this.model});
            this.$(".warning").toggle("slide", {"direction": "up"});
        }
    },
    setSelectedUnselected: function(){
        if(this.model.get("selected") !== undefined && this.model.get("selected")){
            this.$(".select-this-contact").text("Selected").addClass("selected");
        }else{
            this.$(".select-this-contact").text("Select this contact").removeClass("selected");
        }
    },
    getTemplateData: function(){
        var obj = this.model;
        var data = {
          'name': obj.get("first_name") + ' ' + obj.get("last_name"),
          'id': obj.attributes.id,
          'email': obj.get("emails") !== undefined ? obj.get("emails")[0] : "",
          'address': obj.get("addresses") !== undefined ? obj.get("addresses")[0] : "",
          'phone': obj.get("phone") !== undefined ? obj.get("phone")[0] : "",
          'can_edit' : obj.get("can_edit"),
          'hidden' : obj.get("hidden"),
          'notes': obj.get("notes").toString()
        };
        return data;
    },
    render: function(){
        this.parent.el.find(".contacts").prepend(this.el);
        this.$el.append(this.template(this.getTemplateData()));
        this.setSelectedUnselected();
    },
    renderNew: function(){
        this.parent.el.find(".contacts").prepend(this.el);
        this.$el.append(this.template(this.getTemplateData()));
        this.setSelectedUnselected();
    },
    clickContact: function(){
        if(this.model.get("contested") === undefined || !this.model.get("contested")){
            this.$(".select-this-contact").text("Selected").addClass("selected");
            FOIMachine.events.trigger('contactSelected', {contact: this.model});
        }
        return false;
    },
    editContact: function(e){
        var me = this;
        e.preventDefault();
        var target = e.srcElement || e.target;
        target = $(target);
        this.$(".item.contact").hide();
        this.$el.prepend(me.editContactTemplate(me.model.attributes));
        return false;
    },
    saveExistingContact: function(ee){
        var me = this;
        ee.preventDefault();
        me.model.set({
            'first_name': me.$('#edit_input_first_name').val(),
            'last_name': me.$('#edit_input_last_name').val(),
            'hidden': me.$('#edit_input_hidden').prop('checked'),
            'notes': [me.$('#edit_input_notes').val()],
            'titles': [me.$('#edit_input_title').val()],
            'addresses':[me.$('#edit_input_address').val()],
            'emails': [me.$('#edit_input_email').val()],
            'phone': [me.$('#edit_input_phone').val()]
        });
        me.model.save({},{
            success: function(theContact, response, options){
                $('div#editContactDrawer').remove();
                me.$(".item.contact").show();
                FOIMachine.utils.showUserMsg("Contact succesfully updated!");
                me.$el.html(me.template(me.getTemplateData()));
                if(me.model.get("selected") !== undefined && me.model.get("selected"))
                    me.$(".select-this-contact").text("Selected").addClass("selected");
            },
            error: function(one, two, three){
                if(this.xhr === undefined){
                    message = three.xhr.responseText;
                }else {
                    message = this.xhr.responseText;
                }
                FOIMachine.utils.showUserMsg("Failed to create contact: " + message);
            }
        });
        return false; 
    },
    cancelEditContact: function(){
        $('div#editContactDrawer').remove();
        this.$(".item.contact").show();
        return false;
    },
});
var ContactSelectionView = Backbone.View.extend({
    initialize: function(options){
        this.el = $(options.el);
        this.template = _.template(FOIMachine.templates.selectContactTemplate);
        this.editContactTemplate = _.template(FOIMachine.templates.editContactTemplate);
        this.contacts = new ContactCollection();
        this.currentlySelected = [];
        this.parent = options.parent;
        this.agencyId = null;
    },
    events: {
        "click #saveNewContact": "saveNewContact",
        "click a.add-contact-btn": "addNewContact",
        "click #cancelNewContact": "cancelNewContact"
    },
    addNewContact: function(e){
        e.preventDefault();
        this.el.find('.contacts .addContact').toggle();
        return false;
    },
    cancelNewContact: function(e){
        e.preventDefault();
        this.el.find('.contacts .addContact').toggle();
        return false;
    },
    render: function(){
        var me = this;
        //me.$(".contacts").html("");
        me.el.find(".hide-these-contacts").html("");
        me.el.find(".contacts").html(_.template(FOIMachine.templates.addContactTemplate, {
            agencyId: this.agencyId
        }));
        $('#input_dob').datepicker({
            changeYear: true,
            dateFormat: "yy-mm-dd",
            yearRange: "-100:+100"
        });
        if(this.contacts.models.length <= 0){
            me.$(".contacts").append("<span class='no-contacts'>No contacts for this agency</span>").show();
        }
        var me = this;
        _.each(this.contacts.models, function(obj){
            var csv = new ContactSummaryView({
                parent: me,
                model: obj
            });
            csv.render();
        });
        me.el.find(".contacts").append('<a href="#" class="add-contact-btn"><i class="fa fa-plus-circle"></i> Add New Contact</a>');
        me.el.find(".contacts").show("slide", {"direction": "up"});
    },
    saveNewContact: function(e){
        var me = this;
        e.preventDefault();
        var newContact = new Contact({
            first_name : me.el.find('#input_first_name').val(),
            middle_name : me.el.find('#input_middle_name').val(),
            last_name : me.el.find('#input_last_name').val(),
            dob : me.el.find('#input_dob').val(),
            notes : me.el.find('#input_notes').val(),
            titles : [me.el.find('#input_titles').val()],
            emails : [me.el.find('#input_email').val()],
            phone_numbers : [me.el.find('#input_phone').val()],
            addresses : [me.el.find('#input_address').val()],
            agencyId: me.agencyId
        });
        newContact.save({},{
            success: function(theContact, response, options){
                me.el.find('.contacts .addContact').toggle();
                FOIMachine.utils.showUserMsg("Contact succesfully created!");
                var csv = new ContactSummaryView({
                    parent: me,
                    model:newContact 
                });
                csv.render();
                me.$(".no-contacts").remove();
                if(me.parent !== undefined)
                    me.parent.userCanEditContactInMe();
            },
            error: function(one, two, three){
                if(this.xhr === undefined){
                    message = three.xhr.responseText;
                }else {
                    message = this.xhr.responseText;
                }
                FOIMachine.utils.showUserMsg("Failed to create contact: " + message);
            }
        });
        return false;
    },
    getContactsForAgency: function(agencyId){
        var callback = _.bind(this.render, this);
        this.agencyId = agencyId;
        this.contacts.fetch({success: callback, data: {'agencies__id': agencyId}});
    },
    agenciesClose: function(){
        this.el.hide();
    },
    hideMe: function(){
        this.el.hide();
        return "Choose agencies";
    }
});


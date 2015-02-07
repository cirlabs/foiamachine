try{FOIMachine = FOIMachine;}catch(err){FOIMachine = {};}
FOIMachine.events = FOIMachine.events !== undefined ? FOIMachine.events : _.extend({}, Backbone.Events);
FOIMachine.templates = FOIMachine.templates !== undefined ? FOIMachine.templates : {};
FOIMachine.templates.requestSummaryTemplate = ' \
  <div class="item">\
    <span class="add"><a href="#" class="click-request-button" id="<%= id %>">Add</a></span>\
    <div class="to">To: <span><%= agencyName %></span></div>\
    <span id="request-text-id-<%= id %>">About: <%= bodyHTML %></span>\
    <div class="date">Added: <%= dateAdded %></div>\
  </div>\
';
FOIMachine.templates.requestListItemTemplate = '' +
    '<div class="request list-item row">'+
        '<div class="title-dates-status-container row">' +
            '<div class="selectme">'+
                '<input class="request_check" name="requests_to_modify" id="<%= id %>" value="<%= id %>" type="checkbox"/>'+
            '</div>'+
            '<div class="request-item-click" id="i<%= id %>" data-href="<%= detail_url %>">'+
                '<div class="title">'+
                    '<a href="<%= detail_url %>"><%= title %></a>'+
                '</div>'+
                '<div class="status">'+
                    '<span class="status-lbl" style="background-color:<%= status_color %>"><a href="<%= detail_url %>"><%= status_str %></a></span>'+
                '</div>'+
                '<div class="response-date">'+
                    '<% if(status_str !== "Fulfilled") { %> <a href="<%= detail_url %>"> <%= due_date_str %> </a> <% } %>'+
                '</div>'+
            '</div>'+
            '<div class="misc-container row">'+
                '<div class="date-added">'+
                    'Added on <%= date_added_str %>'+
                '</div>'+
                '<div class="privacy">'+
                    '<%= privacy_str %>' + 
                '</div>'+
                '<div class="last-viewed">'+
                    'Last updated on <%= date_updated_str %>' +
                '</div>'+
            '</div>'+
            '<div class="agency-statute-container row">'+
                '<div class="agency">'+
                    '<span class="lbl">Addressed to</span>'+
                        '<%= agency_str %>' +
                    '<span class="lbl">under</span>'+
                        '<%= gov_str %>'+
                '</div>'+
            '</div>'+
            '<div class="tags-container row">'+
                '<span class="lbl">Tags: </span> <%= tag_str %>'+
            '</div>'+
        '</div>'+
    '</div>';
var Request = Backbone.Model.extend({
    idAttribute: "id",
    initialize: function(attributes){
        this.attributes = attributes;
        /*HACK CENTRAL TODO LET TASTYPIE MANAGE RELATIONSHIP SERIALIZATION */
       //this.initRelations();
    },
    initRelations: function(){
        FOIMachine.utils.onloadSelectedContacts = {};
        if(this.attributes.agency !== undefined){
            this.attributes.agency = new Agency(this.attributes.agency);
        }
        if(this.attributes.contacts !== undefined){
            var contacts = [];
            _.each(this.attributes.contacts, function(contact){
                var ele = new Contact(contact)
                contacts.push(ele);
                FOIMachine.utils.onloadSelectedContacts[ele.get("id")] = ele.get("id");
            });
            this.set("contacts", contacts);
        }else{
            this.set("contacts", []);
        }
    },
    hasContact: function(contact){
        return this.get("contacts").filter(function(d){
            if(d.get !== undefined)
                return d.get("id") === contact.get("id");
            return d.id === contact.get("id");
        }).length > 0;
    },
    addAttachment: function(attachment){
        this.attributes.attachments.push(attachment);
    },
    removeAttachment: function(attachmentId){
        this.attributes.attachments = _.reject(this.attributes.attachments, function(obj){
            return obj.id == attachmentId;
        });
    },
    removeAllAttachments: function(){
        this.attributes.attachments = [];
    },
    addContact: function(contact){
        this.attributes.contacts.push(contact);
    },
    getSelectedAgencyId: function(){
        if(this.get("contacts").length > 0)
            return this.get("contacts")[0].getAgencyId();
        return undefined;
    },
    removeContact: function(contactId){
        var contact = _.filter(this.attributes.contacts, function(obj){
            if(obj.get !== undefined)
                return obj.get("id") === contactId;
            return obj.id === contactId;
        })[0];
        this.attributes.contacts = _.reject(this.attributes.contacts, function(obj){
            if(obj.get !== undefined)
                return obj.get("id") === contactId;
            return obj.id === contactId;
        });
        return contact;
    },
    removeAllContacts: function(){
        this.attributes.contacts = [];
    },
    hasMailOnlyContact: function(){
      var only_one = false;      
      this.get("contacts").forEach(function(d){
        if(d.get("addresses") !== undefined && d.get("addresses").length > 0 && d.get("emails") !== undefined && d.get("emails").length < 1)
          only_one = true;
      });
      return only_one;
    },
    canSend: function(){
        if(this.get("contacts").length < 1)
            return false;
        if(this.get("free_edit_body").trim() === "")
            return false;
        return true;
    },
    url: function(){
        var end = '/api/v1/request/'
        if(this.attributes.id !== undefined)
            end = '/api/v1/request/' + this.attributes.id + '/';
        return FOIMachine.utils.constructSafeUrl(end);
    }
});
var ViewableLink = Backbone.Model.extend({
    initialize: function(attributes){
        this.attributes = attributes;
    },
    url: function(){
        var end = '/api/v1/viewablelink/';
        if (this.attributes.id !== undefined)
        {
            end += this.attributes.id + '/';
        }
        return FOIMachine.utils.constructSafeUrl(end);
    }

});

var RequestCollection = Backbone.Collection.extend({
    model: Request,
    initialize: function(models, options){
    },
    url: function(){
        return FOIMachine.utils.constructSafeUrl('/api/v1/request/');
    }
});
var RequestItemView = Backbone.View.extend({
    model: Request,
    class: "item-container",
    events: {
      "click .request-item-click": "navToDetail"
    },
    initialize: function(options){
        if(options.el !== undefined)
            this.el = options.el;
        if(options.model !== undefined)
            this.model = options.model;
        if(options.parent !== undefined)
            this.parent = options.parent;
    },
    render: function(){
        var template = _.template(FOIMachine.templates.requestListItemTemplate);
        var html = template(this.model.attributes);
        this.$el.html(html);
        this.parent.$el.append(html);
        $(".request-item-click#i"+this.model.get("id")).unbind("click").on("click", _.bind(this.navToDetail, this));
    },
    navToDetail: function(){
      var href = this.$el.find(".request-item-click#i" + this.model.get("id")).attr("data-href");
      window.location.href = href;
    }
});
var RequestListView = Backbone.View.extend({
    events: {
        'click .status-filter': 'filterByStatus',
        'click .load-all': 'loadAll'
    },
    loadAll: function(){
      if(this.loadedAll){
        FOIMachine.utils.showUserMsg("It appears we've already loaded all the requests");
        return;
      }
      var me = this;
      this.loadedAll = true;
      var callback = _.bind(this.render, this);
      if(this.groupId !== undefined){
        this.items.fetch({data: {"groups__id": this.groupId, "limit": 1000, "offset": this.curIdx},success: callback, error: function(){
          me.loadedAll = false;
          FOIMachine.utils.showUserMsg("Request failed. Please try again");
        }}); 
      }
    },
    initialize: function(options){
        this.el = options.el;
        this.items = new RequestCollection({});
        this.limit = 5;
        this.curIdx = this.limit;
        this.loadedAll = false;
        var that = this;
        if(options.modelAttributes !== undefined){
          options.modelAttributes.forEach(function(attr){
              var model = new Request({attributes: attr.attrs});
              model.id = attr.attrs.id;//so backbone doesn't think this is a NEW new object
              var detailView = new RequestItemView({el: attr.el, model: model});
              that.items.models.push(model);
          }); 
        }
        if(options.groupId !== undefined){
          var callback = _.bind(this.render, this);
          this.groupId = options.groupId;
          this.items.fetch({data: {"groups__id": options.groupId, "limit": 5},success: callback});
        }
    },
    filterByStatus: function(e){
        var target =  e.srcElement || e.target;
        if($(target).hasClass("selected")){
            $(target).removeClass("selected");
        }else{
            $(target).addClass("selected");
        }
        var selected = this.$(".status-filter.selected");
        var statuses = '';
        selected.each(function(idx, ele){
            if(idx >= selected.length - 1){
                statuses += $(ele).attr("data-status");
            }else{
                statuses += $(ele).attr("data-status") + ",";
            }
        });
        this.$(".request-list-conatiner").html("Loading requests");
        var callback = _.bind(this.renderItems, this);
        this.items.fetch({success: callback, data: {"status__in": statuses}});
    },
    render: function(){
      var that = this;
      if(this.items.models.length < 1){
        this.$el.append("<div class='row'>No requests to show.</div>");
      }else{
        this.$(".load-all").show();
      }
      if(this.loadedAll){
        this.$(".load-all");
      }
      this.items.models.forEach(function(model){
        var view = new RequestItemView({model: model, parent: that});
        view.render();
      });
    }
});
var RequestSelectionView = Backbone.View.extend({
    initialize: function(options){
        this.template = _.template(FOIMachine.templates.requestSummaryTemplate);
        this.el = $(options.el);
        this.requests = new RequestCollection();
        var callback = _.bind(this.render, this);
        this.requests.fetch({success: callback, data:{}});
    },
    render: function(){
        var me = this;
        _.each(this.requests.models, function(obj){
            var agencyName = 'Agency not set';
            if(obj.get("agency") !== undefined)
                agencyName = obj.get("agency").get('name');
            var bodyHTML = 'Unspecified';
            if(obj.get("title") !== undefined && obj.get("title") !== '')
                bodyHTML = obj.get("title");
            data = {
              'dateAdded':obj.get("date_added"),
              'bodyHTML': bodyHTML,
              'id': obj.get("id"),
              'agencyName': agencyName 
            };
            me.el.append(me.template(data));
        });
    },
    toggle: function(){
        if(this.el.css('display') !== 'none'){
            this.el.hide();
            return "Choose a template";
        }
        this.el.show();
        return "Close templates";
    }
});
var RequestCreationView = Backbone.View.extend({
    initialize: function(options){
      if(options === undefined)
        options = this.options;
      this.agencyView = new AgencySelectionView({el: options.agencyEl});
      this.scvParent = $(options.selectedContactsEl);
      this.textAreaEl = options.textArea;
      this.textArea = $(options.textArea);
      this.saveButton = $(options.saveButton);
      this.subjectInput = $(options.subjectInput);
      this.sendButton = $(options.sendButton);
      this.saveAndQuitButton = $(options.saveAndQuitButton);
      this.attachments = $(options.attachments);
      this.sendRequest = false;
      this.fileUploadInput = $(options.fileUploadInput);
      this.editor = FOIMachine.utils.getMediumEditor(this.textAreaEl);
      this.requestDownloadButton = $(options.downloadRequestButton);
      this.promptedDownloadPrinted = false;
      this.locked = false;
      this.contacts = [];

      var me = this;

      this.setRequest();
     
      this.render();
      setInterval(function(){me.updateRequest();}, 60000);
    },
    setRequest: function(){
        //override me
    },
    render: function(){
      FOIMachine.events.on('contactSelected', _.bind(this.contactSelected, this));
      FOIMachine.events.on('contactDeSelected', _.bind(this.contactDeSelected, this));
      FOIMachine.events.on('contactWarningAccepted', _.bind(this.acceptedContactWarning, this));
      var me = this;
      this.textArea.unbind("keyup").on("keyup", function(e){
        var html = FOIMachine.utils.getMediumHtml(me.textAreaEl).trim();
        me.request.set("free_edit_body", html);
      });
      this.subjectInput.unbind("keyup").on("keyup", function(e){
        me.request.set("title", me.subjectInput.val());
      });
      this.fileUploadInput.fileupload({
            dataType: 'json',
            url: '/api/v1/mail/attachment/'
        }).on('fileuploadadd', function(e, data){
            $('#fileUploadStatus').removeClass().addClass('fa fa-spinner');
            $('#save-msg').hide();
        })
        .on('fileuploaddone', function(e, data){
            $('#fileUploadStatus').removeClass().addClass('fa fa-check-square');
            me.request.removeAllAttachments();
            me.request.addAttachment(data.result.files[0]);
            $('#save-msg').show();
            me.renderAttachments();
        }).on('fileuploadfail', function(e, data){
            $('#fileUploadStatus').removeClass().addClass('fa fa-exclamation');
            me.request.removeAllAttachments();
            $('#save-msg').show();
            if (data.messages && data.messages.uploadedBytes){
                FOIMachine.utils.showUserMsg("File size too large (limit is 2mb). Try a smaller attachment.");
            }
            me.renderAttachments();
        });
      this.requestDownloadButton.unbind("click").on("click", function(e){
        me.generate_pdf = true;
        me.updateRequest();
        //me.handleRequestDownload();
        return false;
      });
      this.sendButton.unbind("click").on("click", function(e){
          me.sendRequest = true;
          me.updateRequest();
          return false;
      });
      this.saveButton.unbind("click").on('click', _.bind(this.updateRequest, this));
      this.saveAndQuitButton.unbind("click").on('click', _.bind(this.saveAndQuit, this));
      this.attachments.unbind("click").on("click", ".remove-attachment", function(){
        var $this = $(this);
        var attachmentId = $this.data('attachment');
        me.request.removeAttachment(attachmentId);
        me.renderAttachments();
      });
      var me = this;
      this.renderAttachments();
    },
    addContact: function(contact){
      contact.set("contested", false);
      $(".rnote").hide();
      this.request.addContact(contact);
      contact.set("selected", true);
      var scv = new SelectedContactView({parent: this.scvParent, contact: contact})
      scv.render();
      this.updateRequest();
    },
    contactSelected: function(data, goAhead){
      if(data.errorMsg !== undefined){
        FOIMachine.utils.showUserMsg(data.errorMsg);
        return false;
      }
      if(this.request.get("contacts").length < 1){
        this.addContact(data.contact);
      }else if(this.request.getSelectedAgencyId() !== undefined && this.request.getSelectedAgencyId() === data.contact.getAgencyId()){
        if(this.request.hasContact(data.contact)){
          //we've selected a contact again
          var removedContact = this.request.removeContact(data.contact.get("id"));
          if(removedContact !== undefined){
            //we had a contact selected when the request was loaded
            removedContact.set("selected", false);
          }
          data.contact.set("selected", false);
          this.updateRequest(); 
        }else{
          this.addContact(data.contact);
        }
      }else if(this.request.getSelectedAgencyId() !== data.contact.getAgencyId() && goAhead === undefined){
        //we already have some contacts selected and they are from a different agency, kick off event
        data.contact.set("contested", true);
      }
      return false;
    },
    acceptedContactWarning: function(data){
      $(".select-this-contact").removeClass("selected");
      this.request.get("contacts").forEach(function(d){d.set("selected", false);});
      this.scvParent.empty();
      this.request.removeAllContacts();
      this.addContact(data.contact);
    },
    contactDeSelected: function(data){
      if(this.request !== undefined){
        this.request.removeContact(data.contactId);
        this.updateRequest();
      }
      return false;
    },
    renderAttachments: function(){
        var frag = '';
        if (this.request !== undefined){
            _.each(this.request.attributes.attachments, function(atch){
                frag += '<div class="attachment-wrapper"><a class="attachment" href="' + atch.url + '" target="_blank">';
                frag += '<i class="fa fa-cloud-download"></i>';
                frag += atch.filename;
                frag += '</a>';
                frag += '<i class="remove-attachment fa fa-times-circle" data-attachment="' + atch.id + '"></i></div>';
            });
        }
        this.attachments.html(frag);
    },
    setEditableRequest: function(data){
      this.textArea.html(this.request.get("free_edit_body"));
      this.subjectInput.val(this.request.get("title"));
      var contacts = this.request.get("contacts");
      var me = this;
      _.each(contacts, function(contact){
        var scv = new SelectedContactView({parent: me.scvParent, contact: contact});
        scv.render();
      });
      return false;
    },
    getPrivate: function(){
      //always private, user has more options on request detail page, let them select there this is just for editing
      return true;
    },
    updateRequest: function(addAttrs){
      if(this.request !== undefined){
        this.request.set("private", this.getPrivate());
        this.request.set("free_edit_body", FOIMachine.utils.getMediumHtml(this.textAreaEl).trim());
        this.request.set("title", this.subjectInput.val());
        var message = this.sendRequest ? "Saving and sending..." : "Saving...";
        this.sendButton.removeClass('active');
        FOIMachine.utils.showUserMsg(message);
        this.request.changed = {
          "private": this.getPrivate(),
          "free_edit_body": FOIMachine.utils.getMediumHtml(this.textAreaEl).trim(),
          "title": this.subjectInput.val(),
          "contacts": this.request.get("contacts"),
          "attachments": this.request.get("attachments"),
          "do_send": this.sendRequest,
          "generate_pdf": this.generate_pdf
        };
        if(this.addAttributes !== undefined)
          this.addAttributes();
        this.contacts = this.request.get("contacts");
        this.request.save(this.request.changed, {success: _.bind(this.updateViewOnSave, this), patch:true});
      }
      return false;
    },
    saveAndQuit: function(){
      if(this.request !== undefined){
        this.request.set("private", this.getPrivate());
        this.request.set("free_edit_body", FOIMachine.utils.getMediumHtml(this.textAreaEl).trim());
        this.request.set("title", this.subjectInput.val());
        this.request.save(null, {success: _.bind(this.quit, this), error: function(){
          FOIMachine.utils.showUserMsg("An unexpected error occurred. Please try again.");
        }});
      }
      return false;
    },
    quit: function(){
      window.location = "/requests/" + this.request.get("id") + "/";
      return false;
    },
    autosaveError: function(){
      FOIMachine.utils.showUserMsg("An unexpected error occurred while attempting to auto save your request. We'll keep trying to save it but you may want to press save.");
    },
    handleRequestDownload: function(e){
      //ONLY OPTION IS YES OR CLOSE
      /*
      var me = this;
      if(me.locked){
        FOIMachine.utils.showUserMsg("Still working to create your request...");
        return false;
      }
      */
      //me.request.set("generate_pdf", true);
      //FOIMachine.utils.showUserMsg("Working to create a printable request...");

      /* 
      this.request.changed = {
        "private": this.getPrivate(),
        "free_edit_body": FOIMachine.utils.getMediumHtml(this.textAreaEl).trim(),
        "title": this.subjectInput.val(),
        "contacts": this.request.get("contacts"),
        "attachments": this.request.get("attachments")
      };
      if(this.addAttributes !== undefined)
        this.addAttributes();

      me.locked = true
      //work around bc always_return_data is false for a request and we always need be generating a pdf with most up to date request
      this.request.save(this.request.changed, {
        success: function(){
          FOIMachine.utils.showUserMsg("Fetching download link...");
          var contacts = me.request.get("contacts");
          me.request.fetch({
            data: {'generate_pdf': true},
            success:function(){
              me.request.set("generate_pdf", false);
              FOIMachine.utils.showUserMsg("Created!");
              me.request.set("contacts", contacts);
              me.requestDownloadButton.show();
              var url = me.request.get("request_download_url");
              window.open(url,'_blank');
              me.locked = false;
            },error: function(){
              FOIMachine.utils.showUserMsg("There was an error creating a printable request for you.");
              me.locked = false;
            }
          });
        },
        error: function(){
          FOIMachine.utils.showUserMsg("An unexpected error occurred. Please try again.");
          me.locked = false;
        }
      });
      */
    },
    showDownloadRequest: function(){
      this.requestDownloadButton.show();
      if(!this.promptedDownloadPrinted){
        FOIMachine.utils.showUserMsg("Looks like you have at least one contact without an email. Would you like to download your request to mail it? <span class='yesno'>Yes</span>");
        $(".yesno").on("click", _.bind(this.handleRequestDownload, this));
        this.promptedDownloadPrinted = true;
      }
    },
    autosaveSuccess: function(){
      if(this.request.canSend()){
        this.sendButton.addClass('active');
      }else{
        this.sendButton.removeClass('active');
      }
      if(this.request.hasMailOnlyContact())
        this.showDownloadRequest();
    },
    setGeneratorButton: function(){
      $("#request-generator-btn").attr("href", "/requests/new#request="+this.request.get("id"));
    },
    updateViewOnSave: function(model, response, options){
      this.request.set("contacts", this.contacts);
      if(this.request.get("id") === undefined) {
        var location = options.xhr.getResponseHeader("Location").split("/");
        //server doesn't return values on save so let's parse out the id
        this.request.set("id", location[location.length - 2]);
      }
      window.location = '#request=' + this.request.get("id");

      if(this.generate_pdf){
        this.generate_pdf = false;
        if(this.request.get("request_download_url") !== undefined){
          FOIMachine.utils.showUserMsg("Created!");
          this.requestDownloadButton.show();
          var url = this.request.get("request_download_url");
          window.open(url,'_blank');
        }else{
          FOIMachine.utils.showUserMsg("There was an error creating a printable request for you.");
        }
      }
      this.setGeneratorButton();
      if(this.postSave !== undefined)
        this.postSave();
      if(this.sendRequest){
        this.sendRequest = false;
        if(this.request.get("sent") !== undefined && this.request.get("sent")){
          FOIMachine.utils.showUserMsg('Request sent!');
          window.location = "/requests/" + this.request.get("id") + "/";
          return false;
        }else{
          FOIMachine.utils.showUserMsg('There was an error trying to send your request. Please try again.');
        }
      }else{
        FOIMachine.utils.showUserMsg('Request saved!');
      }
      if(this.request.hasMailOnlyContact())
        this.showDownloadRequest();
      if(this.request.canSend()){
        this.sendButton.addClass('active');
      }else{
        this.sendButton.removeClass('active');
      }
    }
});
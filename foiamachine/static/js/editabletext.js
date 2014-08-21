try{FOIMachine = FOIMachine;}catch(err){FOIMachine = {};}
FOIMachine.events = FOIMachine.events !== undefined ? FOIMachine.events : _.extend({}, Backbone.Events);
FOIMachine.templates = FOIMachine.templates !== undefined ? FOIMachine.templates : {};
FOIMachine.templates.editableMessageTemplate = '' +
    '<input class="<%= cid %>" id="msg-subject" type="text" placeholder="Message Subject"></input>'+
    '<input id="msg-date" type="text" placeholder="Message Date" style="display:none;"></input>'+
    '<div class="<%= cid %> textarea" contenteditable="false"><span class="placeholder">Copy and paste an email response or type an update<span> </div>'+
    '<form class="<%= cid %>" id="fileUploadForm">' + 
         '<%= token %>' + 
         '<button style="position: relative" type="button" id="fileUploadButton" class="btn"><i id="fileUploadStatus"></i>Upload Attachment' + 
         '<input style="opacity: 0; position: absolute; top:0; right: 0; left: 0; bottom: 0" type="file" id="fileUploadInput" name="file"></input>' + 
         '</button>' + 
     '</form>' +
    '<span id="save-msg" class="btn <%= cid %>" data-request="<%=request%>">Save note</span>'+
    '<span id="cancel-msg" class="btn <%= cid %>">Cancel</span>';
FOIMachine.templates.customMailMessageTemplate = '' +
    '<div class="email-header">'+
        '<span class="email-subject"><%=subject%></span>'+
        '<% if( ! was_fwded ){%>'+
            '<b>User added message</b>'+
        '<% }else { %>'+
            'This message was forwarded to this request by <b><%=email_from %></b>'+
        '<% } %>'+
        '<% if(to !== undefined && to.length > 0){ %>'+
            '<span class="email-to">to: <%= to %></span>'+
        '<% } %>'+
        '<% if(cc !== undefined && cc.length > 0){ %>'+
            '<span class="email-to">cc: <%= cc %></span>'+
        '<% } %>'+
        '<span class="email-to">received @: <%= dated %></span>'+
        '<div class="edit-rm-container">'+
            '<span class="remove-msg-btn"><i class="fa fa-times-circle"> Delete</i></span>'+
            '<span class="edit-body btn">Edit note</span><span class="save-edit-body btn">Save note</span><span class="cancel-edit-body btn">Cancel</span>'+
        '</div>'+
    '</div>'+
    '<div class="email-content">'+
        '<div class="textarea saved <%= cid %>">'+
            '<%= body %>'+
        '</div>' +
        '<div></div>'+
        '<div class="attachments">'+
            '<% _.each(attachments, function(attachment){  %>'+
                '<a class="attachment" href="<%= attachment[0]%>"><i class="fa fa-cloud-download"></i> <%= attachment[1] %></a>'+
            '<% }); %>'+
        '</div>'+
    '</div>';


var Message = Backbone.Model.extend({
    initialize: function(attributes){
        this.attributes = attributes;
    },

    url: function(){
        var end = '/api/v1/message/';
        if (this.attributes.id !== undefined && this.attributes.id !== '')
        {
            end += this.attributes.id + '/';
        }
        return FOIMachine.utils.constructSafeUrl(end);

    },
    test: function(){
        var that = this;
        var parent = new Message({
            id: 168
        });
        parent.fetch({
            success: function(){
                that.set({
                    following: 168,
                    body: "TEST MESSAGE",
                    created: "2014-01-21T20:00:00+00:00",
                    dated: "2014-01-21T20:00:00+00:00",
                    direction: "R",
                    email_from: "foo@example.com",
                    reply_to: "foo@example.com",
                    slug: "TEST MSG",
                    subject: "TEST MSG",
                    to: ["shmoo@example.com"],
                    updated: "2014-01-21T20:00:00+00:00"
                });
                that.save({
                    success: function(){
                        console.log(that);

                    },error: function(e){
                        console.log(e);

                    }

                });

            }
        });

    }
});

var MessageCollection = Backbone.Collection.extend({
    model: Message,
    initialize: function(models, options){

    },
    url: function(){ 
        return '/api/v1/message/';
    }
});
var EditableMessagesListView = Backbone.View.extend({
    events: {
        "click #add-msg": "addMsg",
    },
    initialize: function(options){
       this.el = options.el;
       this.messages = new MessageCollection();
       this.request = options.request;
       this.token = options.token;
       var that = this;
       if(options.userMessages){
            options.userMessages.forEach(function(obj){
                var message = new Message({id: obj.id, request: that.request});
                message.id = obj.id;//so backbone doesn't think this is a NEW new object
                message.set("request", that.request);
                //model.on("change", _.bind(that.itemChanged, that));
                that.messages.models.push(message);
                var emv = new EditableMessageView({"parent": that, model: message, token: that.token, request: that.request, el: obj.el});
                emv.textAreaClassName = ".textarea.saved.c"+obj.id;
                emv.setEditor();
                emv.editor.deactivate();
            });
       }
    },
    addMsg: function(){
        var message = new Message({});
        this.messages.models.push(message);
        var emv = new EditableMessageView({"parent": this, model: message, token: this.token, request: this.request});
        emv.render();
        $("#add-msg").hide();
        //this.$(".messages").append(emv.el);
    }
});
var EditableMessageView = Backbone.View.extend({
    className: 'message user-msg',
    model: Message,
    events: {
        "click #save-msg": "saveMsg",
        "click #cancel-msg": "cancelMsg",
        "click .edit-body": "editBody",
        "click .save-edit-body": "saveBody",
        "click .cancel-edit-body": "cancelEdit",
        "click .remove-msg-btn": "deleteMsg"
    },
    initialize: function(options){
        //this.el = options.el;
        this.request = options.request;
        this.token = options.token;
        //this.model = options.model;
        this.cid = this.model.cid;
        this.parent = options.parent;
        if(options.el !== undefined)
            this.el = options.el;
        //this.render();
    },
    setEditor: function(){
        this.editor = FOIMachine.utils.getMediumEditor(this.textAreaClassName);
    },
    render: function(){
        var that = this;
        this.template = _.template(FOIMachine.templates.editableMessageTemplate);
        this.$el.html(this.template({token: this.token, request: this.request, cid: this.model.cid}));
        if(this.parent !== undefined){
            this.parent.$(".messages").append(this.el);
        }

        this.textAreaClassName = "." + this.model.cid + ".textarea";
        this.setEditor();

        this.editor.activate();
        //this.editor.deactivate();
        this.attachmentId = null;

        this.$(".textarea").attr("contenteditable", "true").addClass("editable");
        this.$('#msg-date').datepicker({
            defaultDate: Date()
        });
        this.$('#msg-date').datepicker("setDate", "+0");
        var that = this;
        this.$('#fileUploadInput').fileupload({
            dataType: 'json',
            url: '/api/v1/mail/attachment/'
        }).on('fileuploadadd', function(e, data){
            that.$('#fileUploadStatus').removeClass().addClass('fa fa-spinner');
            that.$('#save-msg').hide();
        })
        .on('fileuploaddone', function(e, data){
            that.$('#fileUploadStatus').removeClass().addClass('fa fa-check-square');
            that.attachmentId = +data.result.files[0].id;
            that.$('#save-msg').show();
        }).on('fileuploadfail', function(e, data){
            that.$('#fileUploadStatus').removeClass().addClass('fa fa-exclamation');
            that.$('#save-msg').show();
            if (data.messages && data.messages.uploadedBytes){
                FOIMachine.utils.showUserMsg("File size too large. Try a smaller attachment.");
            }
        });
    },
    deleteMsg: function(){
        this.model.set("deprecated", new Date());
        FOIMachine.utils.showUserMsg("Deleting...");
        this.model.save({success: _.bind(this.deletedMsg, this), error: function(m, xhr, options){
            FOIMachine.utils.showUserMsg("An error occurred. If the problem persists, email info@foiamachine.org.");
        }});
        this.model.on("change", _.bind(this.deletedMsg, this));
    },
    deletedMsg: function(){
        this.$el.remove();
        FOIMachine.utils.showUserMsg("Message removed");
    },
    saveMsg: function(){
        if(this.model.get("deprecated") !== undefined){
            return this.deletedMsg();
        }
        var content = FOIMachine.utils.getMediumHtml(this.textAreaClassName).trim();
        if(content.length < 1){
            FOIMachine.utils.showUserMsg("Please enter a message before saving.");
            return;
        }
        var content = FOIMachine.utils.getMediumHtml(this.textAreaClassName);
        var theDate = this.$("#msg-date").datepicker('getDate').toISOString();
        var subject = this.$("#msg-subject").val();
        var following = $('.message').data('message');
        var data = {
            created: new Date(),
            dated: theDate,
            direction: "R",
            subject: subject,
            updated: theDate,
            request: this.$('#save-msg').data('request'),
            'body': content
        };
        if (this.attachmentId){
            data.attachments = [this.attachmentId];
        }
        if (following) {
            data.following = following;
        }
        this.model.attributes = data;
        FOIMachine.utils.showUserMsg("Saving...");
        this.model.save({success: _.bind(this.savedMessage, this), error: function(m, xhr, options){
            FOIMachine.utils.showUserMsg("An error occurred. If the problem persists, email info@foiamachine.org.");
        }});
        this.model.on("change", _.bind(this.savedMessage, this));
    },
    savedMessage: function(model, response, options){
        $("#add-msg").show();
        var that = this;
        that.$(".textarea").attr("contenteditable", "false").removeClass("editable").hide();
        that.editor.deactivate();
        that.template = _.template(FOIMachine.templates.customMailMessageTemplate);
        this.model.set("cid", this.cid);
        that.$el.html(that.template(that.model.attributes));
        that.editor = FOIMachine.utils.getMediumEditor(that.textAreaClassName);
        that.editor.deactivate();
        this.$(".save-edit-body").hide();
        this.$(".cancel-edit-body").hide();
        FOIMachine.utils.showUserMsg("Message saved");
    },
    showAddMsg: function(){
        this.$(".textarea").show();
        this.$(".textarea").attr("contenteditable", "true").addClass("editable");
        this.$("#add-msg").hide();
        this.$("#msg-date").show();
        this.$("#msg-subject").show();
        this.$("#fileUploadForm").show();
        this.$("#save-msg").show();
        this.$("#cancel-msg").show();
        this.editor.activate();
    },
    cancelMsg: function(){
        this.$(".textarea").attr("contenteditable", "false").removeClass("editable").hide();
        this.editor.deactivate();
        this.$("#add-msg").show();
        this.$("#msg-date").hide();
        this.$("#msg-subject").hide();
        this.$("#fileUploadForm").hide();
        this.$("#save-msg").hide();
        this.$("#cancel-msg").hide();
        this.$el.remove();
        $("#add-msg").show();
    },
    cancelEdit: function(){
        this.$(".textarea").html(this.model.get("body"));
        this.$(".textarea").attr("contenteditable", "false").removeClass("editable");
        //this.$el.hide();
        this.editor.deactivate();
        this.$(".save-edit-body").hide();
        this.$(".cancel-edit-body").hide();
        this.$(".edit-body").show();
        $("#add-msg").show();
    },
    saveBody: function(){
        var content = FOIMachine.utils.getMediumHtml(this.textAreaClassName).trim();
        this.model.set("body", content);
        FOIMachine.utils.showUserMsg("Saving...");
        this.model.save({success: _.bind(this.savedBody, this), error: function(m, xhr, options){
            FOIMachine.utils.showUserMsg("An error occurred. If the problem persists, email info@foiamachine.org.");
        }});
        this.model.on("change", _.bind(this.savedMessage, this));

    },
    savedBody: function(){
        this.$(".edit-body").hide();
        this.$(".save-edit-body").show();
        this.$(".textarea").attr("contenteditable", "false").removeClass("editable");
        this.editor.deactivate();
    },
    editBody: function(){
        $("#add-msg").hide();
        this.$(".edit-body").hide();
        this.$(".save-edit-body").show();
        this.$(".textarea").attr("contenteditable", "true").addClass("editable");
        this.$(".save-edit-body").show();
        this.$(".cancel-edit-body").show();
        this.editor.activate();
    }
});

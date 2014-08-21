try{FOIMachine = FOIMachine;}catch(err){FOIMachine = {};}
FOIMachine.events = FOIMachine.events !== undefined ? FOIMachine.events : _.extend({}, Backbone.Events);
FOIMachine.templates = FOIMachine.templates !== undefined ? FOIMachine.templates : {};
FOIMachine.templates.feeExemptionItem = '' +
'<div class="published-text <%=type%> <% if (can_edit){ %> editable <% } %>">' +
    '<div class="text">'+
    '<% if(can_edit){ %><span class="remove-btn"><i class="fa fa-times-circle"></i></span> <% } %>'+
    '<% if(can_edit){ %><span class="edit-btn" title="Edit"> <i class="fa fa-pencil-square-o"></i></span> <% } %>'+
    '<% if(can_edit){ %><span class="save-edit" id=""><i class="fa fa-check-square-o"></i></span> <% } %>'+
      '<div class="name textarea" data-field="name"><%=name%></div>' +
      '<div class="description textarea" data-field="description"><%=description%></div>' +
      '<a target="_blank" href="<%=source%>" class="source">Source</a>' +
      '<div class="source textarea" data-field="source"><%=source%></div>'+
    '</div>'+
'</div>';



var FeeOrExemption = Backbone.Model.extend({
    initialize: function(options){
        this.type = options.type;
        if(options.attributes !== undefined)
            this.attributes = options.attributes;
    },
    url: function(){
        var end = '/api/v1/feeorexemption/';
        if(this.attributes.id !== undefined)
            end = '/api/v1/feeorexemption/' + this.attributes.id + '/';
        return FOIMachine.utils.constructSafeUrl(end);
    }
});
var FeeOrExemptionCollection = Backbone.Collection.extend({
    model: FeeOrExemption,
    className: 'item-container',
    initialize: function(options){
    },
    url: function(){
        return FOIMachine.utils.constructSafeUrl('/api/v1/feeorexemption/');
    }
});
var FeeOrExemptionDetailView = Backbone.View.extend({
    model: FeeOrExemption,
    className: "item-container",
    events: {
        'click .text .edit-btn': 'editItem',
        'click .text .save-edit': 'saveItem',
        'click .text .remove-btn': 'removeItem'
    },
    initialize: function(options){
        if(options.el !== undefined)
            this.el = options.el;
        if(options.model !== undefined)
            this.model = options.model;
        if(options.parent !== undefined)
            this.parent = options.parent;
        this.statute_id = options.statute_id
        this.editableFields = ['description', 'source', 'name'];
    },
    render: function(){
        var template = _.template(FOIMachine.templates.feeExemptionItem);
        var html = template(this.model.attributes);
        this.$el.html(html);
        this.parent.$(".container").prepend(this.el);
        //this.$el.html(this.template(this.model.attributes));
        //this.$(".edit-btn").on("click", this.editItem);
    },
    removeItem: function(e){
        this.model.set("deprecated", new Date());
        this.model.save({}, {success: _.bind(this.itemRemoved, this), error: function(m, xhr, options){
            FOIMachine.utils.showUserMsg("An error occurred. If the problem persists, email info@foiamachine.org.");
        }});
    },
    itemRemoved: function(e){
        this.$el.remove();
        FOIMachine.utils.showUserMsg("Item removed");
    },
    editItem: function(e){
        this.$(".text .textarea").addClass("editable").attr("contenteditable", "true");
        this.$(".source").hide();
        this.$(".source.textarea").addClass("editable").attr("contenteditable", "true").show();
        this.$(".edit-btn").hide();
        this.$(".save-edit").show();
        FOIMachine.utils.showUserMsg("Click on the text you want to edit.");
    },
    saveItem: function(e){
        //var target = e.target || e.srcElement;
        //var val = $(target).parent().parent().find("textarea").val();
        //var field = $(target).parent().parent().attr("data-field");
        var name = this.$(".name.textarea").html();
        var description = this.$(".description.textarea").html();
        var source = this.$(".source.textarea").html();
        this.model.set("name", name);
        this.model.set("description", description);
        this.model.set("source", source);
        this.model.save({statute_id: this.statute_id}, {success: _.bind(this.itemSaved, this), error: function(m, xhr, options){
            FOIMachine.utils.showUserMsg("An error occurred. If the problem persists, email info@foiamachine.org.");
        }});
    },
    itemSaved: function(model, response, options){
        var that = this;
        this.$(".text .textarea").removeClass("editable").attr("contenteditable", "false");
        this.$("a.source").show();
        this.$(".source.textarea").removeClass("editable").attr("contenteditable", "false").hide();
        this.$(".edit-btn").show();
        this.$(".save-edit").hide();
        FOIMachine.utils.showUserMsg("Item updated");
    }
});
var FeeOrExemptionListView = Backbone.View.extend({
    events: {
        'click .add-btn': "addItem"
    },
    initialize: function(options){
        this.el = options.el;
        this.items = new FeeOrExemptionCollection({});
        this.statute_id = options.statute_id;
        this.type = options.type;
        var that = this;
        options.modelAttributes.forEach(function(attr){
            var model = new FeeOrExemption({attributes: attr.attrs});
            model.id = attr.attrs.id;//so backbone doesn't think this is a NEW new object
            model.on("change", _.bind(that.itemChanged, that));
            var detailView = new FeeOrExemptionDetailView({el: attr.el, model: model});
            that.items.models.push(model);
        });
    },
    addItem: function(e){
        var model = new FeeOrExemption({
            "name": "Enter a name",
            "description": "Enter a description",
            "source": "http://google.com",
            "typee": this.type == "fee" ? "F" : "E",
            "type": this.type,
            "can_edit": true
        });
        var template = _.template(FOIMachine.templates.feeExemptionItem);
        var html = template(model.attributes);
        var detailView = new FeeOrExemptionDetailView({model: model, parent: this, statute_id: this.statute_id});
        detailView.render();
        detailView.editItem();
        this.items.models.push(model);
        model.on("change", _.bind(this.itemChanged, this));
        this.$(".no-items-msg").remove();
        /*
        model.save({statute_id: this.statute_id}, {success: _.bind(this.itemSaved, this), error: function(m, xhr, options){
            FOIMachine.utils.showUserMsg("An error occurred. If the problem persists, email info@foiamachine.org.");
        }});
        */
    },
    itemChanged: function(model){
        var dep = model.get("deprecated");
        if(dep !== undefined){
            this.items.models = this.items.models.filter(function(mdl){
                return mdl.get("id") !== undefined && mdl.get("id") !== model.get("id");
            });
        }
    },
    itemSaved: function(model, response, options){
        FOIMachine.utils.showUserMsg("Item added");
    }
});
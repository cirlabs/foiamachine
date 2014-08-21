try{FOIMachine = FOIMachine;}catch(err){FOIMachine = {};}
FOIMachine.events = FOIMachine.events !== undefined ? FOIMachine.events : _.extend({}, Backbone.Events);
FOIMachine.templates = FOIMachine.templates !== undefined ? FOIMachine.templates : {};
FOIMachine.templates.addRemoveItemTemplate = '' +
    '<span class="name" id="<%= id %>"><%= name %></span>' +
    '<% if (can_edit){ %><span class="edit-name" id="<%= id %>"><input type="text" name="tag-name" placeholder="Change tag: <%= name %>"></span> <% } %>' +
    '<% if (can_edit){ %><span class="save-edit" id="<%= id %>"><i class="fa fa-check-square"></i></span><% } %>' +
    '<% if (can_edit){ %><span class="edit" id="<%= id %>"><i class="fa fa-pencil-square"></i></span><% } %>'+
    '<% if (can_edit){ %><span class="remove" id="<%= id %>"><i class="fa fa-times-circle"></i></span><% } %>';
FOIMachine.templates.addRemoveGroupItemTemplate = '' +
    '<span class="name" id="<%= id %>"><%= name %></span>' +
    '<% if (can_edit){ %><span class="edit" id="<%= id %>"><i class="fa fa-pencil-square"></i></span><% } %>'+
    '<% if (can_edit){ %><span class="remove" id="<%= id %>"><i class="fa fa-times-circle"></i></span><% } %>' +
    '<div class="switch-container">' +
        '<label class="switch-light switch-candy" onclick="">' +
            '<input type="checkbox" <% if(toggle_to_edit) {%> checked <% } %>>' +
            '<span class="change-access">' +
                '<span>view</span>' +
                '<span>edit</span>' +
            '</span>' +
            '<a></a>' +
        '</label>' +
    '</div>';
var GenericModel = Backbone.Model.extend({
    initialize: function(options){
        this.type = options.type;
        if(options.attributes !== undefined)
            this.attributes = options.attributes;
    },
    url: function(){
        var end = '/api/v1/' + this.type + '/';
        if(this.attributes.id !== undefined)
            end = '/api/v1/' + this.type + '/' + this.attributes.id + '/';
        return FOIMachine.utils.constructSafeUrl(end);
    }
});
var GenericCollection = Backbone.Collection.extend({
    model: GenericModel,
    initialize: function(options){
        this.type = options.type;
    },
    url: function(){
        return FOIMachine.utils.constructSafeUrl('/api/v1/' + this.type);
    },
    getItemNames: function(){
        return this.models.map(function(d){return d.get("name")});
    } 
});
var AddRemoveItemView = Backbone.View.extend({
    className: 'item-container',
    model: GenericModel,
    events: {
        "click .remove": "removeItem",
        "click .edit": "showEditItem",
        "click .change-access": "changeAccess",
        "click .save-edit": "saveEdit"
    },
    initialize: function(options){
        this.type = options.type;
        this.templateToUse = this.type === 'group' ? FOIMachine.templates.addRemoveGroupItemTemplate : FOIMachine.templates.addRemoveItemTemplate;
    },
    changeAccess: function(e){
        var data = {};
        data['action'] = 'change-access';
        FOIMachine.utils.showUserMsg("Saving...");
        this.$el.css('pointer-events', 'none' );
        var that = this;
        this.model.save({data: data}, {success: _.bind(this.accessChanged, this), error: function(model, stuff, objects){
            //reverse whatever setting since I can't stop the toggle from occurring when clicked
            if(that.$('input').is(':checked')){
                that.$('input').prop('checked', false);
            }else{
                that.$('input').prop('checked', true);
            }
            that.$el.css( 'pointer-events', 'all' );
            FOIMachine.utils.showUserMsg("Change failed:" + objects.xhr.responseText);
        }});
    },
    accessChanged: function(e){
        FOIMachine.utils.showUserMsg("Change succeeded");
        this.$el.css( 'pointer-events', 'all' );
    },
    saveEdit: function(e){
        var value = this.$("input").val().trim();
        if(value === "" || value.indexOf("__")==0){
            FOIMachine.utils.showUserMsg("Please enter a valid name. The one you entered appears to be blank or invalid.");
        }else{
            FOIMachine.utils.showUserMsg("Saving...");
            this.model.set("name", value);
            var data = {action: 'rename'};
            this.model.save({data: data}, {success: _.bind(this.updatedName, this), error: FOIMachine.utils.showServerError});
            
        }
    },
    updatedName: function(e){
        this.$(".name").html(this.model.get("name"));
        this.$("save-edit").val("");
        this.$(".name").show();
        this.$(".save-edit").hide();
        this.$(".edit").show();
        this.$(".edit-name").hide();
        FOIMachine.utils.showUserMsg("Successfully updated tag");
    },
    showEditItem: function(e){
        if(this.type === 'group'){
            this.$(".switch-container").show();
        }else{
            this.$(".name").hide();
            this.$(".save-edit").show();
            this.$(".edit").hide();
            this.$(".edit-name").show();
        }
    },
    disassociated: function(e){
        FOIMachine.utils.hideUserMsg();
        this.el.remove();
        var mdl = this.model;
        this.parent.items.models = _.reject(this.parent.items.models, function(it){
            return it.get("id") === mdl.get("id");
        });
    },
    removeItem: function(e){
        var data = {
            'action': 'disassociate',
            'request_id': this.parent.requestId
        };
        FOIMachine.utils.showUserMsg("Removing...");
        this.model.save({data: data}, 
        {success: _.bind(this.disassociated, this), error: FOIMachine.utils.showServerError});
        //todo disassociate me from this models list held by this.parent by fetching new or rejecting me from that list?
    },
    render: function(){
        this.template = _.template(this.templateToUse);
        this.$el.html(this.template(this.model.attributes));
    }
});
var MultiAddRemoveItemsView = Backbone.View.extend({
    initialize: function(options){
        this.requestIds = options.requestIds;
        this.type = options.type;
        this.items = new GenericCollection({type: this.type});
        this.el = $(options.el);
        this.inputEl = $(options.input);
        this.autoCompleteData = options.groupKeyVals;
        this.inputEl.autocomplete({
            source: _.keys(this.autoCompleteData)
        });
        this.addBtnEl = $(options.addButton);
        var callback = _.bind(this.addItem, this);
        this.addBtnEl.unbind("click").bind("click", callback);
        this.fetchRender();
    },
    render: function(){
        var that = this;
        that.el.html("");
        this.inputEl.val("");
        _.each(this.items.models, function(item){
            item.type = that.type;
            if (item.attributes.name.indexOf("__")==0)
            {
                // Hidden item
                return;
            }
            var itemView = new AddRemoveItemView({
                model: item,
                type: item.type
            });
            itemView.parent = that;
            itemView.render();
            that.el.append(itemView.el);
        });
    },
    fetchRender: function(){
        FOIMachine.utils.hideUserMsg();
        var callback = _.bind(this.render, this);
    },
    itemUpdated: function(model){
        FOIMachine.utils.hideUserMsg();
        location.reload();
    },
    addGenericItem: function(callback){
        var itemNames = this.items.getItemNames();
        var counter = 1;
        // e.g. "tag set 1"
        var itemName = '__shared ' + this.type + " set " + counter;
        while(_.has(this.autoCompleteData, itemName))
        {
            counter++;
            itemName = '__shared ' + this.type + " set " + counter;
        }
        var model = new GenericModel({name: itemName, request_ids: this.requestIds});
        model.type = this.type;
        FOIMachine.utils.showUserMsg("Saving...");
        var data = {};
        model.save({data: {}}, {success: function(){callback(itemName);}, error: FOIMachine.utils.showServerError});
    },
    addItem: function(e){
        var itemName = this.inputEl.val();
        if(this.items.getItemNames().indexOf(itemName) !== -1){
            FOIMachine.utils.showUserMsg("You've already added that!");
            return -1;
        }
        if (itemName.indexOf("__") == 0)
        {
            FOIMachine.utils.showUserMsg("This is not a valid name");
            return -1;
        }
        var data = {};
        if(_.keys(this.autoCompleteData).indexOf(itemName) !== -1){
            var itemId = this.autoCompleteData[itemName];
            var model = new GenericModel({id: itemId, name: itemName, request_ids: this.requestIds});
            model.id = itemId;
            model.type = this.type;
            data['action'] = 'associate';
            FOIMachine.utils.showUserMsg("Saving...");
            model.save({data: data}, {success: _.bind(this.itemUpdated, this), error: FOIMachine.utils.showServerError });
        }else{
            var model = new GenericModel({name: itemName, request_ids: this.requestIds});
            model.type = this.type;
            FOIMachine.utils.showUserMsg("Saving...");
            model.save({data: data}, {success: function(){location.reload();}, error: FOIMachine.utils.showServerError });
        }
    }

});
var AddRemoveItemsView = Backbone.View.extend({
    initialize: function(options){
        this.requestId = options.requestId;
        this.type = options.type;
        this.items = new GenericCollection({type: this.type});
        this.el = options.el;
        this.inputEl = this.$("input");
        this.autoCompleteData = options.groupKeyVals;
        this.inputEl.autocomplete({
            source: _.keys(this.autoCompleteData)
        });
        //this.addBtnEl = $(options.addButton);
        //var callback = _.bind(this.addItem, this);
        //this.addBtnEl.unbind("click").bind("click", callback);
        this.fetchRender();
    },
    events: {
        "click .add-btn": "addItem",
        "keypress :input": "addItemKey"
    },
    render: function(){
        var that = this;
        that.$(".shared-container").html("");
        this.inputEl.val("");
        _.each(this.items.models, function(item){
            if (item.attributes.name.indexOf("__") == 0)
            {
                return;
            }
            item.type = that.type;
            var itemView = new AddRemoveItemView({
                model: item,
                type: item.type
            });
            itemView.parent = that;
            itemView.render();
            that.$(".shared-container").append(itemView.el);
        });
    },
    fetchRender: function(){
        FOIMachine.utils.hideUserMsg();
        var callback = _.bind(this.render, this);
        this.items.fetch({success: callback, data: {"request_id": this.requestId}});
    },
    itemUpdated: function(model){
        FOIMachine.utils.hideUserMsg();
        var itemView = new AddRemoveItemView({
            model: model,
            type: this.type
        });
        itemView.parent = this;
        itemView.render();
        this.$(".shared-container").append(itemView.el);
        this.items.push(model);
        this.inputEl.val("");
    },
    addItemKey: function(e){
        if (e.keyCode == 13) {
            e.preventDefault();
            this.addItem();
        }
    },
    addItem: function(){
        var itemName = this.inputEl.val();
        if(this.items.getItemNames().indexOf(itemName) !== -1){
            FOIMachine.utils.showUserMsg("You've already added that!");
            return -1;
        }
        var data = {};
        if(_.keys(this.autoCompleteData).indexOf(itemName) !== -1){
            var itemId = this.autoCompleteData[itemName];
            var model = new GenericModel({id: itemId, name: itemName, request_id: this.requestId});
            model.id = itemId;
            model.type = this.type;
            data['action'] = 'associate';
            FOIMachine.utils.showUserMsg("Saving...");
            model.save({data: data}, {success: _.bind(this.itemUpdated, this), error: FOIMachine.utils.showServerError });
        }else{
            //STEVE: Are we creating an item? (this applies to tags only currently)
            //SHANE: This creates a new object rather than associate an existing object (stored in the autocomplete dict), which is automagically associated with the request
            var model = new GenericModel({name: itemName, request_id: this.requestId});
            model.type = this.type;
            FOIMachine.utils.showUserMsg("Saving...");
            model.save({data: data}, {success: _.bind(this.fetchRender, this), error: FOIMachine.utils.showServerError });
        }
    }
});

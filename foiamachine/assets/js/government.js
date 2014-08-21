try{FOIMachine = FOIMachine;}catch(err){FOIMachine = {};}
FOIMachine.events = FOIMachine.events !== undefined ? FOIMachine.events : _.extend({}, Backbone.Events);
FOIMachine.templates = FOIMachine.templates !== undefined ? FOIMachine.templates : {};
FOIMachine.templates.governmentSummaryTemplate = '\
  <div class="item">\
    <a href="#" class="edit-government-button" data-governmentid="<%= id %>">\
        <i class="edit-government fa fa-pencil-square"></i>\
    </a>\
    <a href="#" class="click-government-button" id="<%= id %>">Select</a>\
    <span id="request-text-id-<%= id %>"><%= name %></span>\
    <form class="editGovernmentForm">\
        <div class="formRow">\
            <label>Government name</label>\
            <input class="input_name" value="<%= name %>" />\
        </div>\
        <div class="formRow">\
            <label>Government level</label>\
                <select class="select_level">\
                    <option value="I" <% if (level == "I") { %>selected <% } %> >International</option>\
                    <option value="S" <% if (level == "S") { %>selected <% } %> >Supernational</option>\
                    <option value="0" <% if (level == "0") { %>selected <% } %> >National</option>\
                    <option value="1"  <% if (level == "1") { %>selected <% } %> >State/Province</option>\
                    <option value="2" <% if (level == "2") { %>selected <% } %> >County or Similar</option>\
                    <option value="3" <% if (level == "3") { %>selected <% } %> >City/Municipality</option>\
                </select>\
        </div>\
          <br />\
          <button data-governmentid="<%= id %>" type="button" class="btn saveExistingGovernment"> Save</button>\
          <button type="button" class="btn cancelExistingGovernment">Cancel</button>\
    </form>\
  </div>\
';

var Government = Backbone.Model.extend({
    initialize: function(attributes){
        this.attributes = attributes;
    },
    url: function(){
        if (this.attributes.id !== undefined)
        {
            return '/api/v1/governments/' + this.attributes.id + '/';
        }
        return '/api/v1/governments/';

    }

});

var GovernmentCollection = Backbone.Collection.extend({
    model: Government,
    initialize: function(models, options){

    },
    url: function(){ 
        return '/api/v1/governments/';
    }

});

var GovernmentSelectionView = Backbone.View.extend({
    initialize: function(options) {
        this.template = _.template(FOIMachine.templates.governmentSummaryTemplate);
        this.el = $(options.el);
        this.governments = new GovernmentCollection();
        var callback = _.bind(this.render, this);
        this.governments.fetch({success: callback, data: {
            limit: 1000
        },
        
        error: function(model, response, objects) {
            var message = JSON.parse(objects.xhr.responseText);
            FOIMachine.utils.showUserMsg(message);
        }});
        this._governments = [];
        this.parent = options.parent;
    },
    events: {
        "keyup #agency-search-box": "search",
        "click #close-drawer" : "hideMe",
        "click .click-government-button" : "select",
        "click .edit-government-button" : "edit",
        "click .cancelExistingGovernment" : "hideForm",
        "click .saveExistingGovernment" : "saveForm"

    },
    hideForm : function(e){
        var target = e.srcElement || e.target;
        target = $(target);
        while(!target.hasClass('item')) {
            target = target.parent();
        }
        target.find('.editGovernmentForm').hide();
        e.preventDefault();
        return false;

    },
    saveForm: function(e){ 
        var target = e.srcElement || e.target;
        target = $(target);
        var thisId = target.data('governmentid');
        var me = this;
        var model = _.find(me.governments.models, function(model){
            return +model.attributes.id === thisId;
        });
        var $form = target.parent();
        model.set({
            name : $form.find('.input_name').val(),
            level : $form.find('.select_level').val()
        });
        model.save({}, {
            success: function(model, response, options) {
                $form.hide();
                FOIMachine.utils.showUserMsg('Updated');
                me.render(me._governments);


            },

            error: function(model, response, options) {
                var message = JSON.parse(objects.xhr.responseText);
                FOIMachine.utils.showUserMsg(message);

            }

        });

        e.preventDefault();
        return false;
    },
    edit: function(e) {
        var target = e.srcElement || e.target;
        target = $(target);
        while(!target.hasClass('item')) {
            target = target.parent();
        }
        target.find('.editGovernmentForm').show();
        e.preventDefault();
        return false;

    },
    select: function(e) {
        var target = e.srcElement || e.target;
        var me = this;
        target = $(target);
        var thisId = parseInt(target.attr('id'));
        var model = _.find(me.governments.models, function(model){
            return model.attributes.id === thisId;
        });
        FOIMachine.events.trigger('governmentSelected', {request: model});
        return false;

    },
    search: function(e) {
        var origTarget = e.srcElement || e.target;
        var letters = $(origTarget).html().replace("&nbsp;", "").replace("<br>", "");
        var collection = _.filter(this.governments.models, function(governments){
            var govfields = government.get("name").toLowerCase() + agency.get("nation").toLowerCase();
            var searchstr = letters.toLowerCase();
            return govfields.search(searchstr) !== -1;
        });
        var retval = {
            'models': collection
        };
        this.render(retval);
    },
    back: function(){
        this.render(this._governments);
    },
    render: function(collection) {
        this._governments = collection;
        var models = (_.isUndefined(collection) || collection.models.length <= 0) && $("#agency-search-box").html() === "" ? this.governments.models : collection.models;
        models = _.sortBy(models, function(gov){return gov.attributes.name;});
        var me = this;
        me.$('.item').remove();
        _.each(models, function(obj){
            me.el.append(me.template(obj.attributes));

        });
    },
    toggle: function(){
        if(this.el.css('display') !== 'none'){
            this.el.hide();
            FOIMachine.events.trigger("governmentSelectionClosed", {});
            return "Choose a government";
        }
        this.el.show();
        return "Close governments`";
    },
    hideMe: function(){
        this.el.hide();
        return "Choose a government";
    }



});

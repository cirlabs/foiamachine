try{FOIMachine = FOIMachine;}catch(err){FOIMachine = {};}
FOIMachine.events = FOIMachine.events !== undefined ? FOIMachine.events : _.extend({}, Backbone.Events);
FOIMachine.templates = FOIMachine.templates !== undefined ? FOIMachine.templates : {};
FOIMachine.templates.govListingTemplate = '<div class="government-listing" id="government-listing-<%= id %>">' +
' <%= name %> <span data-id="<%= id %>" class="gov-delete-btn" title="Delete"> <i class="fa fa-times-circle"></i><span>' +
'</div>';

var Statute = Backbone.Model.extend({
    initialize: function(options){
        this.type = options.type;
        if(options.attributes !== undefined)
            this.attributes = options.attributes;
    },
    url: function(){
        var end = '/api/v1/statute/';
        if(this.attributes.id !== undefined)
            end = '/api/v1/statute/' + this.attributes.id + '/';
        return FOIMachine.utils.constructSafeUrl(end);
    }
});
var StatuteCollection = Backbone.Collection.extend({
    model: Statute,
    initialize: function(options){
    },
    url: function(){
        return FOIMachine.utils.constructSafeUrl('/api/v1/statute/');
    }
});
var StatuteDetailView = Backbone.View.extend({
    className: 'statute',
    model: Statute,
    events: {
        "click .short-title-container .edit-btn": "editShortTitle",
        "click .short-title-container .save-edit": "saveShortTitle",
        "click .basic-stats-container .stats-row-one .four .edit-btn": "editDaysTillDue",
        "click .basic-stats-container .stats-row-one .four .save-edit": "saveDaysTillDue",
        "click .law-text-container .edit-btn": "editLawText",
        "click .law-text-container .save-edit": "saveLawText",
        "click .law-text-container .toggle-btn.hide": "coverLongLawText",
        "click .law-text-container .toggle-btn.show": "showLongLawText",
        "click .delete-btn" : "toggleDeleted",
        "click .gov-delete-btn" : "deleteGov",
        "click .gov-add-btn" : "addGov",
        "click .add-government-btn, #cancelNewGovernment" : "toggleAddGovernmentDrawer",
        "click #saveNewGovernment" : "saveGov"

    },
    toggleAddGovernmentDrawer : function (e){
        var that = this;
        e.preventDefault();
        $('#addGovernmentDrawer').toggle();
        return false;
    },
    addGov : function(){
        this.gsv.toggle();
        

    },
    saveGov : function(e){
        e.preventDefault();
        var name = $('#input_name').val();
        var level = $('#select_level').val();
        var gov = new Government({
            name: name,
            level: level
        });
        var that = this;
        gov.save({}, {
            success: function(){
                that.$('#gov-view .item:first').before('<div class="item"><a href="#" class="click-government-button" id="' + gov.attributes.id + '"> Select</a> ' + 
                    '<span id="request-text-id-' + gov.attributes.id + '">' + gov.attributes.name + '</a></div>');
                that.delegateEvents();
                that.gsv.delegateEvents();
                that.gsv.governments.add(gov);
            },

            error: function(model, response, objects) {
                var message = JSON.parse(objects.xhr.responseText);
                FOIMachine.utils.showUserMsg(message);
            }
          }
        );
        $('#addGovernmentDrawer').hide();
        
        return false;
        

    },
    deleteGov: function(e){
        var statute = this.model;
        var that = this;
        var $target = $(e.currentTarget);
        var whichGov = $target.data('id');

        var govs = _.without(statute.get("governments"), whichGov);

        statute.set("governments", govs);

        statute.save({},{ 
            success: function(model, xhr, options){ 
                $target.parent().remove();
                
            },
            error: function(model, response, objects) {
                var message = JSON.parse(objects.xhr.responseText);
                FOIMachine.utils.showUserMsg(message);
            }
        });

    },
    toggleDeleted: function(){
        var statute = this.model;
        var that = this;
        statute.set("deleted", !statute.attributes.deleted);
        statute.save({

        }, {
            success: function(){
            if (statute.attributes.deleted) {
                
                FOIMachine.utils.showUserMsg("This statute will be only visible to editors.");
                that.$('.delete-btn').text('Show this statute');
            }
            else {
                FOIMachine.utils.showUserMsg("This statute will be visible.");
                that.$('.delete-btn').text('Hide this statute');
            }
        }, 
        
        error: function(model, response, objects) {
            var message = JSON.parse(objects.xhr.responseText);
            FOIMachine.utils.showUserMsg(message);
        }
      });
    },
    initialize: function(options){
        this.model = new Statute({attributes: options.modelAttributes});
        this.model.id = options.modelAttributes.id;//give model an id so it does a puts and not a post (create)
        this.el = options.el;
        this.gsv = new GovernmentSelectionView({
            el: $('#gov-view'),
            parent: this
        });
        var lawTextClassName = this.el + " .textarea";
        this.editor = FOIMachine.utils.getMediumEditor(lawTextClassName);
        this.editor.deactivate();
        this.govListingTemplate = _.template(FOIMachine.templates.govListingTemplate);
        FOIMachine.events.on('governmentSelected', _.bind(this.governmentTemplateSelected, this));
    },
    render: function(){
        this.$(".short-title-container input").toggle();
        this.$(".short-title-container h1").toggle();       
        this.$(".short-title-container .edit-btn").toggle();
        this.$(".short-title-container .save-edit").toggle();
        this.gsv.render();
    },
    governmentTemplateSelected: function(data) {
        var govs = this.model.get("governments");
        var me = this;
        if(data.request !== undefined){
            if (_.contains(govs, +data.request.attributes.id))
            {
                return;
            }

            govs.push(+data.request.attributes.id);
            this.model.set("governments", govs);
        }
        this.model.save({}, {
            success: function(un, deux, trois){
                me.$('.gov-container').append(me.govListingTemplate(data.request.attributes));
            }, 
            error: function(model, response, objects) {
                var message = JSON.parse(objects.xhr.responseText);
                FOIMachine.utils.showUserMsg(message);
            }

        });

    },
    editLawText: function(e){
        this.$(".law-text-container span").toggle();
        this.showLongLawText(true);
        this.$(".law-text-container .published-text .text .textarea").addClass("editable").attr('contenteditable','true');
        this.editor.activate();
    },
    saveLawText: function(){
        var val = this.$(".law-text-container .published-text .text .textarea").html();
        if(val !== ""){
            this.model.set("text", val);
            this.model.save({}, {success: _.bind(this.lawTextSaved, this), 
                error: function(model, response, objects) {
                    var message = JSON.parse(objects.xhr.responseText);
                    FOIMachine.utils.showUserMsg(message);
                }
            
            
            });
        }else{
            FOIMachine.utils.showUserMsg("Please enter a value");
        }
    },
    lawTextSaved: function(){
        this.$(".law-text-container span").toggle();
        this.$(".toggle-btn.show").hide();
        this.$(".law-text-container .published-text .text .textarea").removeClass("editable").attr('contenteditable','false');
        this.editor.deactivate();
        FOIMachine.utils.showUserMsg("Statute updated");
    },
    editDaysTillDue: function(e){
        this.$(".basic-stats-container .stats-row-one .four span").toggle();
        this.$(".basic-stats-container .stats-row-one .days-till-due.textarea").addClass("editable").attr("contenteditable", "true");
        FOIMachine.utils.showUserMsg("Please enter a valid number. Use -1 (or less) for statutes that do not list a reasonable response time.");
    },
    saveDaysTillDue: function(){
        var val = this.$(".basic-stats-container .stats-row-one .days-till-due.textarea").text();
        if(val !== "" && !isNaN(parseInt(val))){
            val = parseInt(val) < 0 ? -1 : parseInt(val);
            this.model.set("days_till_due", val);
            this.model.save({}, {success: _.bind(this.daysTillDueSaved, this), error: function(m, xhr, options){
                FOIMachine.utils.showUserMsg("An error occurred. If the problem persists, email info@foiamachine.org.");
            }});
        }else{
            FOIMachine.utils.showUserMsg("Please enter a valid number");
        }
    },
    daysTillDueSaved: function(){
        var val = this.$(".basic-stats-container .stats-row-one .days-till-due.textarea").html();
        if(val !== "" && !isNaN(parseInt(val))){
            if(parseInt(val) < 0)
                this.$(".basic-stats-container .stats-row-one .days-till-due.textarea").html("NA");
        }
        this.$(".basic-stats-container .stats-row-one .four span").toggle();   
        this.$(".basic-stats-container .stats-row-one .days-till-due.textarea").removeClass("editable").attr("contenteditable", "false");
        FOIMachine.utils.showUserMsg("Statute updated");
    },
    editShortTitle: function(e){
        this.$(".short-title-container .short-title.textarea").addClass("editable").attr('contenteditable','true');
        this.$(".short-title-container .edit-btn").toggle();
        this.$(".short-title-container .save-edit").toggle();
    },
    saveShortTitle: function(e){
        var val = this.$(".short-title-container .short-title.textarea").text();
        if(val !== ""){
            this.model.set("short_title", val);
            this.model.save({}, {success: _.bind(this.shortTitleSaved, this), error: function(m, xhr, options){
                FOIMachine.utils.showUserMsg("An error occurred. If the problem persists, email info@foiamachine.org.");
            }});
        }else{
            FOIMachine.utils.showUserMsg("Please enter a value");
        }
    },
    shortTitleSaved: function(){
        this.$(".short-title-container .short-title.textarea").removeClass("editable").attr('contenteditable','false');
        this.$(".short-title-container .edit-btn").toggle();
        this.$(".short-title-container .save-edit").toggle();
        //this.$(".short-title-container h1").html(this.model.get("short_title"));
        FOIMachine.utils.showUserMsg("Statute saved");
    },
    showLongLawText: function(editing){
        var pTags = $(".law-text.textarea p");
        pTags.each(function(idx, ptag){
            $(ptag).removeClass("hidden-lawtext");
        });
        this.$(".toggle-btn.show").hide();
        if(editing === undefined || !(editing === true)){
            this.$(".toggle-btn.hide").show();
        }else{
            this.$(".toggle-btn.hide").hide();
        }
    },
    coverLongLawText: function(){
        var pTags = $(".law-text.textarea p");
        var maxWordCount = 200;
        var wordCount = 0;
        this.$(".toggle-btn.show").hide();
        this.$(".toggle-btn.hide").hide();
        pTags.each(function(idx, ptag){
            var text = $(ptag).text();
            wordCount += text.split(' ').length;
            if(wordCount > maxWordCount)
                $(ptag).addClass("hidden-lawtext");
        });
        if(wordCount > maxWordCount)
            this.$(".toggle-btn.show").show();
    }

});

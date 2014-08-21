try{FOIMachine = FOIMachine;}catch(err){FOIMachine = {};}
FOIMachine.events = FOIMachine.events !== undefined ? FOIMachine.events : _.extend({}, Backbone.Events);
FOIMachine.templates = FOIMachine.templates !== undefined ? FOIMachine.templates : {};
FOIMachine.templates.userTemplate = ''+
    '<div class="userName">'+
        '<span><%= username %></span>'+
        '<span class="name" id="<%= id %>"><%= name %></span>' +
        '<% if (can_edit){ %><span class="edit auser" data-userid="<%= id %>"><i class="fa fa-pencil-square"></i></span><% } %>'+
        '<% if (can_edit){ %><span class="remove" data-userid="<%= id %>"><i class="fa fa-times-circle"></i></span><% } %>' +
        '<div class="switch-container i<%= id %>">' +
            '<label class="switch-light switch-candy" onclick="">' +
                '<input type="checkbox" <% if(toggle_to_edit) {%> checked <% } %>>' +
                '<span class="change-access" data-userid="<%= id %>">' +
                    '<span>view</span>' +
                    '<span>edit</span>' +
                '</span>' +
                '<a></a>' +
            '</label>' +
        '</div>'+
    '</div>';
FOIMachine.templates.groupTemplate = ''+
    '<div class="groupContainer">'+
        '<div class="groupName"><span class="name group-name"><%= name %></span>' +
            '<% if(can_edit) { %>'+
            '<span class="edit-name" id="<%= id %>"><input type="text" name="tag-name" placeholder="Change group: <%= name %>"></span>' +
            '<span class="save-edit" id="<%= id %>"><i class="fa fa-check-square-o"></i> Save</span>' +
            '<span class="cancel-edit" id="<%= id %>"><i class="fa fa-undo"></i> Cancel</span>' +
            '<span class="edit groupz" id="<%= id %>"><i class="fa fa-pencil-square-o"></i> Edit group name</span>'+
            '<div class="remove-container">'+
                '<span class="remove-group" id="<%= id %>"><i class="fa fa-times-circle"></i> Delete group</span>' +
                '<div class="rm-confirm-container">Are you sure? <span class="remove-confirm yes green">Yes</span><span class="remove-confirm no green">No</span></div>' +
            '</div>'+
            '<% } %>'+
        '</div>' +
        '<div class="add-list-users">'+
            '<div class="group-subhed">Users in this group:</div>'+
            '<div class="users">'+
                '<% _.each(users, function(user){ %>'+
                    '<% user["can_edit"] = can_edit %>'+
                    '<% print(userTemplate(user)) %>'+
                '<% }); %>'+
            '</div>'+
            '<% if(can_edit) { %><div class="addUserForm">'+
                '<span class="">Add users to this group: </span>'+
                '<select class="addUserSelect"></select>'+
                '<span class="addUserButton">Add user</span>'+
            '</div> <%}%>'+
        '</div>'+
    '</div>'+
    '<div class="requests-container request-list" id="i<%= id %>">'+
        '<div class="header-note"><span class="">Requests shared with this group</span> <span class="load-all">Show all requests</span></div>'+
        '<div class="header row">'+
            '<div class="selectme"><input type="checkbox" id="check_all_requests"/></div>'+
            '<div class="name">Subject</div>'+
            '<div class="status">Status</div>'+
            '<div class="response-due">Response due</div>'+
        '</div>'+
    '</div>';

var User = Backbone.Model.extend({
    url: function(){
        var end = '/api/v1/user/'
        if(this.attributes.id !== undefined)
            end = '/api/v1/user/' + this.attributes.id + '/';
        return FOIMachine.utils.constructSafeUrl(end);
    }
});
var UserCollection = Backbone.Collection.extend({
    initialize: function(){
        this.fetch();

    },
    model: User,
    url: function(){
        return FOIMachine.utils.constructSafeUrl('/api/v1/user');
    },
    asAutocompleteList: function(){
        var retModels = _.reject(this.models, function(obj){ return obj.get("id") == -1 });
        return _.map(retModels, function(obj){
            return {
                    label: obj.get("username"),
                    value: obj.get("id")
                   };

        });
    }
});
var Group = Backbone.Model.extend({
    initialize: function(options){
        if(options !== undefined)
            this.attributes = options;
    },
    addUser: function(user){
        var users = this.get("users");
        if (_.find(users, function(obj){
            return obj.username == user.username;
        }))
        {
            return;
        }
        this.get("users").push(user);
    },
    removeUser: function(userid){
        this.set("users", _.reject(this.get("users"), function(obj){
            return obj.id == userid;
        }));
    },
    url: function(){
        var end = '/api/v1/group/';
        if(this.attributes.id !== undefined)
            end = '/api/v1/group/' + this.attributes.id + '/';
        return FOIMachine.utils.constructSafeUrl(end);
    }
});

var GroupCollection = Backbone.Collection.extend({
    model: Group,
    url: function(){
        return FOIMachine.utils.constructSafeUrl('/api/v1/group');
    }
});
var GroupView = Backbone.View.extend({
    tagName : "div",
    className: "group",
    events: {
        "click .remove": "removeUser",
        "click .remove-group": "confirmDelete",
        "click .adduser": "showAddUser",
        "click .addUserButton" : "addUser",
        "click .edit.groupz": "showEditItem",
        "click .edit.auser": "editUserPerms",
        "click .remove-confirm.yes": "removeGroup",
        "click .remove-confirm.no": "noConfirm",
        "click .change-access": "changeAccess",
        "click .save-edit": "saveEdit",
        "click .cancel-edit": "cancelEdit"
    },
    initialize: function(){
        this.template = _.template(FOIMachine.templates.groupTemplate);
        this.userTemplate = _.template(FOIMachine.templates.userTemplate);
    },
    editUserPerms: function(e){
        var target = e.srcElement || e.target;
        var userId = $(target.parentNode).attr("data-userid");
        this.$('.switch-container.i'+userId).show();
    },
    confirmDelete: function(e){
        this.$('.rm-confirm-container').show();
    },
    noConfirm: function(e){
        this.$('.rm-confirm-container').hide();
    },
    changeAccess: function(e){
        var target = e.srcElement || e.target;
        var userId = $(target.parentNode).attr("data-userid");
        var data = {};
        data['action'] = 'chown';
        data['user_id'] = userId;
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
    addUser: function(){
        var that = this;
        var userID = this.$el.find("select.addUserSelect").val();
        var user = this.parent.users.where({id: parseInt(userID)})[0];
        this.model.addUser(user.attributes);
        if(this.model.get("data") !== undefined){
            delete this.model.attributes.data;
        }
        this.saveAndRenderNewUser();
        return false;
    },
    groupRemoved: function(e){
        this.$el.remove();
        FOIMachine.utils.showUserMsg("Group deleted.");
    },
    removeGroup: function(e){
        FOIMachine.utils.showUserMsg("Removing group...");
        this.model.destroy({success: _.bind(this.groupRemoved, this), error: FOIMachine.utils.showServerMsg});
    },
    showEditItem: function(e){
        this.$(".name").hide();
        this.$(".save-edit").show();
        this.$(".cancel-edit").show();
        this.$(".edit.groupz").hide();
        this.$(".edit-name").show();
    },
    cancelEdit: function(e){
        this.$(".name").show();
        this.$(".save-edit").hide();
        this.$(".edit.groupz").show();
        this.$(".edit-name").hide();
        this.$(".cancel-edit").hide();
    },
    updatedName: function(e){
        this.$(".name.group-name").html(this.model.get("name"));
        this.$("save-edit").val("");
        this.$(".name").show();
        this.$(".save-edit").hide();
        this.$(".edit.groupz").show();
        this.$(".edit-name").hide();
        this.$(".cancel-edit").hide();
        FOIMachine.utils.showUserMsg("Successfully updated tag");
    },
    saveEdit: function(e){
        var value = this.$("input").val().trim();
        if(value === ""){
            FOIMachine.utils.showUserMsg("Please enter a valid name. The one you entered appears to be blank.");
        }else{
            FOIMachine.utils.showUserMsg("Saving...");
            this.model.set("name", value);
            var data = {action: 'rename'};
            this.model.save({data: data}, {success: _.bind(this.updatedName, this), error: FOIMachine.utils.showServerError});
        }
    },
    showAddUser: function() {
        this.$el.find('div.addUserSelect').show();
    },
    saveAndRender: function() {
        var that = this;
        this.model.save(this.model.attributes, {
            success: function(model){
                that.model = model;
                that.parent.render();
                that.showAddUser();
            },
            error: function(one,two,three){
                FOIMachine.utils.showUserMsg("Error adding user");
            } 
        });

    },
    saveAndRenderNewUser: function() {
        var that = this;
        this.model.save(this.model.attributes, {
            success: function(model){
                that.model = model;
                //that.parent.render();
                //that.showAddUser();
                that.$('.users').empty();
                model.get("users").forEach(function(usr){
                    usr.can_edit = model.get("can_edit");
                    that.$(".users").append(that.userTemplate(usr));
                });
            },
            error: function(one,two,three){
                FOIMachine.utils.showUserMsg("Error adding user");
            } 
        });

    },
    render: function(){
        this.model.attributes.userTemplate = _.template(FOIMachine.templates.userTemplate);
        this.$el.html(this.template(this.model.attributes));
    },
    removeUser: function(e){
        var target = e.srcElement || e.target;
        var userId = $(target.parentNode).attr("data-userid");
        if(_.keys(this.model.attributes).indexOf("data") !== -1)
            delete this.model.attributes['data'];
        this.model.removeUser(userId);
        this.saveAndRender();
    }

});
var GroupCollectionView = Backbone.View.extend({
    initialize: function(options){
        var that = this;
        this.userId = options.userId;
        this.el = $('#groups');
        this.groups = new GroupCollection();
        this.users = new UserCollection();
        this.users.fetch({
            success: function() {
                that.fetchRender();
            }
        });
    },
    fetchRender: function(){
        var callback = _.bind(this.render, this);
        FOIMachine.utils.showUserMsg("Loading groups....");
        if(this.userId !== undefined){
            this.groups.fetch({success: callback, data: {'user_id': this.userId}} );
        }else{
            this.groups.fetch({success: callback, data: {}});
        }

    },
    renderNewGroup: function(group){
        this.groups.models.push(group);
        var groupView = new GroupView({
            model: group
        });
        groupView.parent = this;
        groupView.render();
        this.el.prepend(groupView.el);
        var acl= this.users.asAutocompleteList();
        var selectInnerHTML = "";
        _.each(acl, function(item){
            selectInnerHTML += '<option value="' + item.value + '">' + item.label + '</option>';

        });
        $('.addUserSelect').html(selectInnerHTML);
    },
    render: function(){
        var that = this;
        that.el.html("");
        var ids = [];
        _.each(this.groups.models, function(group){
            var groupView = new GroupView({
                model: group

            });
            ids.push(group.get("id"));
            groupView.parent = that;
            groupView.render();
            that.el.append(groupView.el);

        });
        FOIMachine.events.trigger('groupsLoaded', {groupIds: ids});
        var acl= this.users.asAutocompleteList();
        var selectInnerHTML = "";
        _.each(acl, function(item){
            selectInnerHTML += '<option value="' + item.value + '">' + item.label + '</option>';

        });
        $('.addUserSelect').html(selectInnerHTML);
        FOIMachine.utils.showUserMsg("Groups loaded");


    }
});

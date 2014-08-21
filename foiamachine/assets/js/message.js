try{FOIMachine = FOIMachine;}catch(err){FOIMachine = {};}
FOIMachine.events = FOIMachine.events !== undefined ? FOIMachine.events : _.extend({}, Backbone.Events);
FOIMachine.templates = FOIMachine.templates !== undefined ? FOIMachine.templates : {};

var Message = Backbone.Model.extend({
    initialize: function(attributes){
        this.attributes = attributes;
    },

    url: function(){
        var end = '/api/v1/message/';
        if (this.attributes.id !== undefined)
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

(function() {//thanks https://gist.github.com/mashingan/3873386
  Backbone.Model.prototype._save = Backbone.Model.prototype.save;
  Backbone.Model.prototype.save = function (attrs, options) {
    var that = this;
    if (!options) {
      options = {};
    }
    if (this.savingNewRecord) {
      // store or replace last PUT request with the latest version, we can safely replace old PUT requests with new ones
      // but if there are callbacks from a previous PUT request, we need to make sure they are all called as well
      _(['success', 'error']).each(function (event) {
        // convert all callbacks to a single array of callbacks)
        var existingCallbacks = that.putQueue ? that.putQueue.options[event] : [];
        options[event] = _.compact(existingCallbacks.concat(options[event]));
      });
      this.putQueue = {
        attributes:_.extend({}, that.attributes, attrs),
        options:options
      };
    } else {
      if (this.isNew()) {
        // saving a new record so we need to wait for server to respond and assign an ID before the model is saved again
        this.savingNewRecord = true;
        // store the old callback and overwrite so we can catch the success/error event when savint this model
        _(['success', 'error']).each(function (event) {
          var oldEventCallback = options[event];
          options[event] = function (model, response, options) {
            that.savingNewRecord = false;
            // check if callback for this model save exists and if so execute the callback
            if (oldEventCallback) {
              oldEventCallback.call(this, model, response, options);
            } else if ('success' === event) {
              that.trigger('sync', that, response, options);
            } else if ('error' === event) {
              var resp = model === that ? response : model;
              that.trigger('error', that, resp, options);
            }
 
            // if there is a PUT waiting to fire, fire it now
            if (that.putQueue) {
              // as PUT builds up callbacks as arrays, lets create a callback which executes all the callbacks
              _(['success', 'error']).each(function (callBackEvent) {
                var callbacks = _.clone(that.putQueue.options[callBackEvent]);
                that.putQueue.options[callBackEvent] = function (model, response) {
                  var callbackThis = this;
                  _(callbacks).each(function (callback) {
                    callback.call(callbackThis, model, response);
                  })
                };
              });
              return Backbone.Model.prototype.save.call(that, _.extend({}, that.attributes, that.putQueue.attributes), that.putQueue.options);
            }
          };
        });
      }
      return Backbone.Model.prototype._save.call(this, attrs, options);
    }
  };
}());

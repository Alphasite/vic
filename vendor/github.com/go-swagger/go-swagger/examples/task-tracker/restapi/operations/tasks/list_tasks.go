package tasks

// This file was generated by the swagger tool.
// Editing this file might prove futile when you re-run the generate command

import (
	"net/http"

	"github.com/go-swagger/go-swagger/httpkit/middleware"
)

// ListTasksHandlerFunc turns a function with the right signature into a list tasks handler
type ListTasksHandlerFunc func(ListTasksParams) middleware.Responder

// Handle executing the request and returning a response
func (fn ListTasksHandlerFunc) Handle(params ListTasksParams) middleware.Responder {
	return fn(params)
}

// ListTasksHandler interface for that can handle valid list tasks params
type ListTasksHandler interface {
	Handle(ListTasksParams) middleware.Responder
}

// NewListTasks creates a new http.Handler for the list tasks operation
func NewListTasks(ctx *middleware.Context, handler ListTasksHandler) *ListTasks {
	return &ListTasks{Context: ctx, Handler: handler}
}

/*ListTasks swagger:route GET /tasks tasks listTasks

Lists the tasks

Allows for specifying a number of filter parameters to
narrow down the results.
Also allows for specifying a **sinceId** and **pageSize** parameter
to page through large result sets.


*/
type ListTasks struct {
	Context *middleware.Context
	Handler ListTasksHandler
}

func (o *ListTasks) ServeHTTP(rw http.ResponseWriter, r *http.Request) {
	route, _ := o.Context.RouteInfo(r)
	var Params = NewListTasksParams()

	if err := o.Context.BindValidRequest(r, route, &Params); err != nil { // bind params
		o.Context.Respond(rw, r, route.Produces, route, err)
		return
	}

	res := o.Handler.Handle(Params) // actually handle the request

	o.Context.Respond(rw, r, route.Produces, route, res)

}

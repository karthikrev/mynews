function connect_to_db(){
	var influxdb = new InfluxDB()
	influxdb['hosts'][0] = '33.33.33.33'	
	influxdb['database'] = 'newsdb'
	influxdb['port'] = 8086;
	return influxdb;	
}


function initialize_widgets(client, $scope, $q) {
	//query = "select time, date_published, lead_image_url, title, url, excerpt, content  from /.*/"
	query = "select * from /.*/ limit 6"
    $q.when(influxdb.query(query)).then(function(result){
    	// FOR EACH TABLE ie NEWS DOMAIN
    	angular.forEach(result, function(news_provider){
    		console.log(news_provider)    		    		
    		function I(str) { return news_provider.columns.indexOf(str) }    		
    		$scope.news.push(
    			{'name': news_provider.name, 'widgets': 
    			$.map(news_provider.points, 
    				function(p) { 
    					return {
    						'title': p[I('title')], 
	    					'img': p[I('lead_image_url')], 
	    					'content': p[I('content')],
	    					'table': news_provider.name, 
	    					'news_link':p[I('news_link')]
	    				} 
    				}
    			)       
    		})
    	});
    })    
}

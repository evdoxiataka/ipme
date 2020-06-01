HOVER_CODE="""
        const data = {'x': [], 'y': [], 'isIn': []}        
        data['x']=source.data.x
        data['y']=source.data.y
        for (var i = 0; i<data['x'].length;i++){
            data['isIn'].push(0)
        }
        const indices = cb_data.index.indices
        for (var i = 0; i < indices.length; i++) {            
            const start = indices[i]
            data['isIn'][start]=1      
        }
        source.data = data
    """
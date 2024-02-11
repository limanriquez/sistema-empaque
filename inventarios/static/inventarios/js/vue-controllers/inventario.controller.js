const { createApp } = Vue;

createApp({
    
    delimiters:['{[{','}]}'],
    data() {
        return {
        prueba: "Hello Vue!",
        };
    },
    components: {
       
    },
    methods: {
       
    }
    
}).mount("#inventario");
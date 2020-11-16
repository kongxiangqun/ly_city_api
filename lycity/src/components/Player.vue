<template>
    <div class="player">
      <div id="player">

      </div>
    </div>
</template>

<script>
export default {
  name:"Player",
  data () {
    return {

    }
  },


  mounted() {  //如果需要对标签进行一些加工处理，然后再放数据时，需要用mounted这个钩子函数，如果单纯的是获取数据，添加到数据属性中
                // 那么用created方法

    this.get_video_data();

  },

  methods: {
        get_video_data(){
          let user_name = localStorage.username || sessionStorage.username;
        let token = localStorage.token || sessionStorage.token;
        console.log(this.$route.params.vid)
          let self = this;
        // 引入js提供的一个对象
        var player = polyvPlayer({
          wrap: '#player',
          // 宽度 通过document设置 -300 留出来一个大纲
          width: document.documentElement.clientWidth - 300,
          // 高度
          height: document.documentElement.clientHeight,
          vid: this.$route.params.vid,
          // forceH5: true,

          // code: user_name,
          // polyv提供的方法
          playsafe:  (vid, next) =>{
            console.log(self)
            // 先要token
            self.$axios.get(`${self.$settings.Host}/course/polyv/token/?vid=${self.$route.params.vid}`,{
              headers:{
              'Authorization':'jwt ' + token
              }
            }).then((res)=>{
              // {‘token’:'asasfd'}
              // next就是想polyv发请求要数据的
              next(res.data.token);

            }).catch((error)=>{

            })


          }
        });
      }
  },
  computed: {
  }
}
</script>

<style scoped>
</style>

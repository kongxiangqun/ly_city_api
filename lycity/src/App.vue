<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
  created() {
    window.addEventListener('beforeunload',()=>{
      console.log('页面要刷新啦！！！,赶紧保存数据！！！！');
      sessionStorage.setItem('cart_length',this.$store.state.cart_length);

    })
  }
}
</script>

<style>

</style>

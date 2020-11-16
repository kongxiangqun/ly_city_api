import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import Login from '@/components/Login'
import Register from '@/components/Register'
import Course from "../components/Course";
import Detail from "../components/Detail";
import Cart from "../components/Cart";
import Order from '@/components/Order';
import Success from '@/components/Success';
import Myorder from '@/components/Myorder';
import Player from '@/components/Player';


Vue.use(Router)

export default new Router({
  mode:'history',
  routes: [
    {
      path: '/',
      name: 'aaa',
      component: Home
    },
    {
      path: '/home',
      name: 'bbb',
      component: Home
    },
    {
      path: '/user/login',
      // name: 'bbb',
      component: Login
    },
    {
      path: '/user/register',
      // name: 'bbb',
      component: Register
    },
    {
      path: '/course',
      // name: 'Home',
      component: Course
    },
    {
      path: '/course/detail/:id/',   // /course/detail/1/   this.$route.params.id
      // name: 'Home',
      component: Detail
    },
    {
      path: '/cart/',   // /course/detail/1/   this.$route.params.id
      // name: 'Home',
      component: Cart
    },
    {
      path: '/order/',   // /course/detail/1/   this.$route.params.id
      // name: 'Home',
      component: Order
    },
    {
      path: '/payment/result/',   // /course/detail/1/   this.$route.params.id
      // name: 'Home',
      component: Success
    },
    {
      path: '/myorder/',   // /course/detail/1/   this.$route.params.id
      // name: 'Home',
      component: Myorder
    },
    {
      path: '/myorder/',   // /course/detail/1/   this.$route.params.id
      // name: 'Home',
      component: Myorder
    },
    {
      path: '/polyv/player/:vid',   // /course/detail/1/   this.$route.params.vid
      // name: 'Home',
      component: Player
    },
  ]
})

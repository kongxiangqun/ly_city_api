
export default {
  //Host:"http://www.lyapi.com:8001",// server address
  Host:"http://www.kxq.xyz:81",
  check_login(ths){
      let token = localStorage.token || sessionStorage.token;
      //console.log(this.token);
      console.log('>>>>>',token);
      //console.log('>>>>>',ths.$axios);

      if (token){

        ths.$axios.post(`${this.Host}/users/verify/`,{
            token:token,
          }).then((res)=>{
            //console.log('xxxxxxxxxxxxxxxxxxxxxxx')

            ths.token = token;
            console.log('ooooooooooooooo',ths.token);
            // return 值拿不到。。。

          }).catch((error)=>{
            //console.log(error)
            //.log('ssssssssssssssssssssss')
            ths.token = false;
            sessionStorage.removeItem('token');
            sessionStorage.removeItem('username');
            sessionStorage.removeItem('id');
            localStorage.removeItem('token');
            localStorage.removeItem('username');
            localStorage.removeItem('id');
          })


      } else {
        ths.token = false
      }

    }
}

import styled from 'styled-components';
import purp01 from '../../assets/images/67.png';
import "./about.css";
const SectionWrapper = styled.section`
  min-height: 100vh;
  width: 100vw;
  position: relative; 
  display: flex;
  margin: 0 auto;
  color: white;
  font-family: 'Albert Sans', sans-serif;

`;


const LeftContainer = styled.div`
  top: 10%;
  left: 5%;
  position: absolute;
  text-transform:uppercase; 
  font-family: boldgod;
`; 

const BannerComponent = styled.div`
 
`;
const Container = styled.div`
 
`;

const About = () => {
  return (
    <SectionWrapper id="fixed-target" className="about">
      

      <LeftContainer
        data-scroll
        data-scroll-delay=".15"
        data-scroll-speed="1"
        style={{ transform: 'translate3d(0, 0, 0)' }}
      >
       <p className="how-work">How it works</p>
       <p className="more-thn"><span className="more-yell">More </span>than just  <br />
        a DASHBOARD
       </p> 
  <p className="meta-des">
   Our AI model predicts potential<span className="nft-yell">flight delays in advance,</span> explains the top reasons behind them, and <span className="art-one"> </span><span className="art-two"></span> <br />
   sends instant alerts to your dashboard — so you can act before disruptions happen..
  </p>
      </LeftContainer>
      <Container id="up">
      <BannerComponent>
          <img src={purp01} className="purp-pic"
            alt="Purple NFT artwork"
            data-scroll
            data-scroll-direction="horizontal"
            data-scroll-speed="8"
            data-scroll-target="#up"
            style={{ transform: 'translate3d(0, 0, 0)' }}
          >
          </img>
      </BannerComponent>
      </Container>
      
      
    </SectionWrapper>
  );
};

export default About;

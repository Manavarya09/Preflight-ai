import styled from 'styled-components';
import { motion } from 'framer-motion';
// import car01 from "../assets/images/24.png";
// import car02 from "../assets/images/24.png";
// import car03 from "../assets/images/24.png";
import ric01 from "../assets/images/25.png";
import ric02 from "../assets/images/26.png";
import ric03 from "../assets/images/27.png";
import hvr01 from "../assets/images/28.png";
import hvr02 from "../assets/images/18a.png";
import hvr03 from "../assets/images/18b.png";
import waterm from "../assets/images/29.png";
import "./cover.css";
import "./carousel.css";
import "./carousel-two.css";
const SectionWrapper = styled.section`
  min-height: 100vh;
  width: 100%;
  position: relative;
  
  
`;


const TitleWrapper = styled(motion.div)`
  position: absolute;
  top: 22%;
  left: 3%;
  z-index: 8;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
  gap: 0.5rem;
  div {
    display: flex;
    flex-direction: column;
    gap: 0;
  }
  
`;



const LeftTitleWrapper = styled(motion.div)`
  position: absolute;
  z-index: 8;
  top: 56%;
  left: 3%;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  gap: 2rem;
`;
const Container = styled.div`
   
`;
const LeftContainer = styled.div`
     top: 45%;
     left: 3%;
      display: flex;
     position: absolute;
     gap: 0.8rem;
     z-index: 9;
`;
const RightContainer = styled.div`


`;

const containerVariants = {
  hidden: {
    opacity: 0,
  },
  show: {
    opacity: 1,
    transition: {
      delayChildren: 5,
      staggerChildren: 0.3,
    },
  },
};

const itemVariants = {
  hidden: {
    opacity: 0,
  },
  show: {
    opacity: 1,
  },
};

const CoverVideo = () => {
  return (
    <SectionWrapper>
      <TitleWrapper
        initial="hidden"
        animate="show"
        variants={containerVariants}
      >
        <div>
          <motion.h1
            variants={itemVariants}
            data-scroll
            data-scroll-delay=".15"
            data-scroll-speed="3"
            style={{ transform: 'translate3d(0, 0, 0)' }}
          >
            <p className="welcome">welcome to <span className="meta-yell">preflight ai</span></p>
            <p className="cover-head-vid">Predict <br />
            flight <span className="suit-yell">delays</span>
           </p>
            <p className="scan-me" style={{marginTop: '1.2rem'}}>
              
              — <span style={{color: 'whitesmoke'}}>write before they happen.</span>
            </p>
          </motion.h1>
        </div>
      </TitleWrapper>


      <LeftTitleWrapper
        initial="hidden"
        animate="show"
        variants={containerVariants}
      >
        <motion.div variants={itemVariants}>
          <p className="scan-me">Real-time risk scores and explanations<br />
         from MCP Flight Ops data (weather, gate, ATC) <span className="arrn">&#x2193;</span></p>
        </motion.div>
        
        <motion.div 
          variants={itemVariants}
          style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '0.5rem'}}
        >
      
        </motion.div>
      </LeftTitleWrapper>
      {/* <Container>
      <div className="carousel">
        <img className="rot-pic-one" src={car01} alt="" />
        <img className="rot-pic-two" src={car02} alt="" />
        <img className="rot-pic-three" src={car03} alt="" /> 
        <img className="rot-pic-one" src={car01} alt="" />
        <img className="rot-pic-two" src={car02} alt="" />
      </div>
      </Container> */}
      <RightContainer>
      <div className="carousel-two">
        <img className="ric" src={ric01} alt="" />
        <img className="ric" src={ric02} alt="" />
        <img className="ric" src={ric03} alt="" />
        <img className="ric" src={ric01} alt="" />
        <img className="ric" src={ric02} alt="" />
       </div>
      </RightContainer>
     
    </SectionWrapper>
  );
};

export default CoverVideo;
